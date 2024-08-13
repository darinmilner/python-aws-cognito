create table if not exists testdata(
  id INTEGER,
  unit_num INTEGER,
  street_num INTEGER,
  street_name VARCHAR(255),
  suburb_name VARCHAR(255),
  suburb_postcode INTEGER,
  area_size DOUBLE PRECISION,
  area_unit VARCHAR(255),
  contract_date DATE,
  settlement_date DATE,
  sold_price INTEGER,
  zoning VARCHAR(255),
  property_nature VARCHAR(255)
);