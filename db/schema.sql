-- Supabase database schema for IPNet website

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Members table
CREATE TABLE IF NOT EXISTS members (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    member_id TEXT UNIQUE NOT NULL, -- Original string ID from JSON
    name TEXT NOT NULL,
    join_date DATE,
    location TEXT,
    avatar TEXT,
    bio TEXT,
    contact_preference TEXT,
    is_public BOOLEAN DEFAULT true,
    node_name TEXT,
    node_public_key TEXT,
    social_links JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Nodes table
CREATE TABLE IF NOT EXISTS nodes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    node_id TEXT UNIQUE NOT NULL, -- Original string ID from JSON
    public_key TEXT,
    name TEXT NOT NULL,
    member_id TEXT REFERENCES members(member_id),
    area TEXT NOT NULL,
    latitude DECIMAL(10, 7), -- Latitude coordinate
    longitude DECIMAL(10, 7), -- Longitude coordinate
    location_description TEXT, -- Location description
    hardware TEXT,
    antenna TEXT,
    elevation INTEGER,
    show_on_map BOOLEAN DEFAULT true,
    is_public BOOLEAN DEFAULT true,
    is_online BOOLEAN DEFAULT false,
    is_testing BOOLEAN DEFAULT false,
    last_seen TIMESTAMP WITH TIME ZONE,
    mesh_role TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_members_member_id ON members(member_id);
CREATE INDEX IF NOT EXISTS idx_members_is_public ON members(is_public);
CREATE INDEX IF NOT EXISTS idx_nodes_node_id ON nodes(node_id);
CREATE INDEX IF NOT EXISTS idx_nodes_member_id ON nodes(member_id);
CREATE INDEX IF NOT EXISTS idx_nodes_area ON nodes(area);
CREATE INDEX IF NOT EXISTS idx_nodes_is_public ON nodes(is_public);
CREATE INDEX IF NOT EXISTS idx_nodes_is_online ON nodes(is_online);
CREATE INDEX IF NOT EXISTS idx_nodes_show_on_map ON nodes(show_on_map);
CREATE INDEX IF NOT EXISTS idx_nodes_location ON nodes(latitude, longitude);

-- Create updated_at trigger function with secure search path
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER
SECURITY DEFINER
SET search_path = public
LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

-- Add updated_at triggers
DROP TRIGGER IF EXISTS update_members_updated_at ON members;
CREATE TRIGGER update_members_updated_at
    BEFORE UPDATE ON members
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_nodes_updated_at ON nodes;
CREATE TRIGGER update_nodes_updated_at
    BEFORE UPDATE ON nodes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security
ALTER TABLE members ENABLE ROW LEVEL SECURITY;
ALTER TABLE nodes ENABLE ROW LEVEL SECURITY;

-- Create policies for public read access
CREATE POLICY "Allow public read access to public members" ON members
    FOR SELECT USING (is_public = true);

CREATE POLICY "Allow public read access to public nodes" ON nodes
    FOR SELECT USING (is_public = true);

-- Create policies for authenticated write access (optional - for admin interface later)
CREATE POLICY "Allow authenticated users to insert members" ON members
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "Allow authenticated users to update members" ON members
    FOR UPDATE USING (auth.role() = 'authenticated');

CREATE POLICY "Allow authenticated users to insert nodes" ON nodes
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "Allow authenticated users to update nodes" ON nodes
    FOR UPDATE USING (auth.role() = 'authenticated');
