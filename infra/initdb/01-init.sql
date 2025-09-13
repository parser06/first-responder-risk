-- Initialize First Responder Risk Monitoring Database
-- This script sets up the database with PostGIS extension and initial configuration

-- Enable PostGIS extension for geospatial data
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Create a dedicated user for the application (optional)
-- CREATE USER first_responder_app WITH PASSWORD 'app_password';
-- GRANT ALL PRIVILEGES ON DATABASE first_responder_risk TO first_responder_app;

-- Create indexes for better performance (will be created by SQLAlchemy, but good to have)
-- These will be created when the application starts and runs migrations

-- Create a function to calculate distance between two points
CREATE OR REPLACE FUNCTION calculate_distance(
    lat1 DOUBLE PRECISION,
    lon1 DOUBLE PRECISION,
    lat2 DOUBLE PRECISION,
    lon2 DOUBLE PRECISION
) RETURNS DOUBLE PRECISION AS $$
BEGIN
    RETURN ST_Distance(
        ST_GeogFromText('POINT(' || lon1 || ' ' || lat1 || ')'),
        ST_GeogFromText('POINT(' || lon2 || ' ' || lat2 || ')')
    );
END;
$$ LANGUAGE plpgsql;

-- Create a function to find officers within a radius
CREATE OR REPLACE FUNCTION find_officers_within_radius(
    center_lat DOUBLE PRECISION,
    center_lon DOUBLE PRECISION,
    radius_meters DOUBLE PRECISION
) RETURNS TABLE(
    officer_id UUID,
    name VARCHAR,
    badge_number VARCHAR,
    distance_meters DOUBLE PRECISION
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        o.id,
        o.name,
        o.badge_number,
        calculate_distance(center_lat, center_lon, l.latitude, l.longitude) as distance
    FROM officers o
    JOIN location_data l ON o.id = l.officer_id
    WHERE l.recorded_at = (
        SELECT MAX(recorded_at) 
        FROM location_data l2 
        WHERE l2.officer_id = o.id
    )
    AND calculate_distance(center_lat, center_lon, l.latitude, l.longitude) <= radius_meters
    ORDER BY distance;
END;
$$ LANGUAGE plpgsql;

-- Insert some sample data for development
INSERT INTO officers (id, badge_number, name, department, phone, email, is_active, is_on_duty, device_id, app_version)
VALUES 
    (gen_random_uuid(), 'PD001', 'John Smith', 'Police Department', '+1-555-0101', 'john.smith@pd.gov', true, true, 'device_001', '1.0.0'),
    (gen_random_uuid(), 'FD002', 'Sarah Johnson', 'Fire Department', '+1-555-0102', 'sarah.johnson@fd.gov', true, true, 'device_002', '1.0.0'),
    (gen_random_uuid(), 'EMT003', 'Mike Davis', 'Emergency Medical', '+1-555-0103', 'mike.davis@emt.gov', true, false, 'device_003', '1.0.0')
ON CONFLICT (badge_number) DO NOTHING;

COMMIT;
