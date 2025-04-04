-- Ensure tables exist before creating indexes
PRAGMA foreign_keys = ON;


-- Index for Customers
CREATE INDEX IF NOT EXISTS idx_customers_city ON Customers(City);



-- Index for Orders
CREATE INDEX IF NOT EXISTS idx_orders_customer ON Orders(CustomerID);



-- Index for Products
CREATE INDEX IF NOT EXISTS idx_products_category ON Products(CategoryID);


-- Index for OrderDetails (make sure OrderDetails exists!)
CREATE INDEX IF NOT EXISTS idx_orderdetails_product ON "Order Details"(ProductID);
CREATE INDEX IF NOT EXISTS idx_orderdetails_order ON "Order Details"(OrderID);