-- 1. XÓA CÁC BẢNG CŨ (Cẩn thận: sẽ xóa hết data đang có trong các bảng này)
DROP TABLE IF EXISTS daily_district_stats CASCADE;
DROP TABLE IF EXISTS properties CASCADE;
DROP TABLE IF EXISTS locations CASCADE;
DROP TABLE IF EXISTS property_types CASCADE;

-- ==========================================
-- 2. TẠO BẢNG DANH MỤC
-- ==========================================

-- Bảng Loại Bất động sản
CREATE TABLE property_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

INSERT INTO property_types (name) VALUES 
    ('Căn hộ / Chung cư'),
    ('Nhà ngõ / Hẻm'),
    ('Nhà mặt phố'),
    ('Đất nền / Liền kề'),
    ('Biệt thự');

-- Bảng Địa lý (Tỉnh/Thành, Quận/Huyện, Phường/Xã)
CREATE TABLE locations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    city VARCHAR(100) NOT NULL,
    district VARCHAR(100) NOT NULL,
    ward VARCHAR(100),
    CONSTRAINT unique_location UNIQUE NULLS NOT DISTINCT (city, district, ward)
);

-- ==========================================
-- 3. TẠO BẢNG DỮ LIỆU CHÍNH (Đã update Image & Seller)
-- ==========================================

CREATE TABLE properties (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    location_id UUID NOT NULL REFERENCES locations(id) ON DELETE RESTRICT,
    property_type_id INT NOT NULL REFERENCES property_types(id) ON DELETE RESTRICT,
    
    source_url TEXT NOT NULL UNIQUE, 
    source_site VARCHAR(50) NOT NULL, 
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    
    price BIGINT NOT NULL,
    area NUMERIC(10, 2) NOT NULL,
    price_per_m2 NUMERIC(12, 2) NOT NULL,
    
    bedrooms INT,
    bathrooms INT,
    
    -- THÊM MỚI: Mảng chứa các đường link hình ảnh (Array of Strings)
    image_urls TEXT[] DEFAULT '{}',
    videos TEXT[] DEFAULT '{}',
    
    -- THÊM MỚI: Thông tin người bán / Môi giới
    seller_name VARCHAR(255),
    seller_phone VARCHAR(50),      -- Lưu dạng string để phòng trường hợp web ẩn số: "0901***"
    seller_avatar TEXT,            -- Link avatar người bán
    seller_type VARCHAR(50),       -- Phân loại: 'Cá nhân', 'Môi giới', 'Dự án'
    longitude VARCHAR(50), 
    latitude VARCHAR(50), 
    
    is_active BOOLEAN DEFAULT TRUE,  
    posted_at TIMESTAMPTZ,           
    scraped_at TIMESTAMPTZ DEFAULT NOW(), 
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Bảng Thống kê giá theo ngày 
CREATE TABLE daily_district_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    location_id UUID NOT NULL REFERENCES locations(id) ON DELETE CASCADE,
    property_type_id INT NOT NULL REFERENCES property_types(id) ON DELETE CASCADE,
    
    record_date DATE NOT NULL,
    avg_price_per_m2 NUMERIC(12, 2) NOT NULL,
    total_listings INT NOT NULL,
    
    CONSTRAINT unique_daily_stat UNIQUE (location_id, property_type_id, record_date)
);

-- ==========================================
-- 4. TẠO INDEXES (TỐI ƯU HÓA TRUY VẤN)
-- ==========================================

CREATE INDEX idx_properties_location ON properties(location_id);
CREATE INDEX idx_properties_type ON properties(property_type_id);
CREATE INDEX idx_properties_price_per_m2 ON properties(price_per_m2);
CREATE INDEX idx_properties_scraped_at ON properties(scraped_at);
CREATE INDEX idx_properties_is_active ON properties(is_active);

-- THÊM INDEX: Tìm kiếm theo số điện thoại (Hữu ích sau này nếu muốn check 1 môi giới đăng bao nhiêu bài)
CREATE INDEX idx_properties_seller_phone ON properties(seller_phone);

CREATE INDEX idx_stats_location_date ON daily_district_stats(location_id, record_date);

-- ==========================================
-- 5. FUNCTION & TRIGGER TỰ ĐỘNG CẬP NHẬT `updated_at`
-- ==========================================

CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_properties_modtime
    BEFORE UPDATE ON properties
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();