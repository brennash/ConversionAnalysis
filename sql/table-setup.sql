CREATE TABLE conversions
(
	conversionSID INT AUTO_INCREMENT NOT NULL,
	week DATETIME NOT NULL,
	site VARCHAR(2) NOT NULL,
	visitcountry VARCHAR(3) NOT NULL,
	entrypage VARCHAR(64) NOT NULL,
	subtype VARCHAR(64) NOT NULL,
	device VARCHAR(12) NOT NULL,
	visits INT NOT NULL,
	signups INT NOT NULL,
	orders INT NOT NULL,
	PRIMARY KEY(conversionSID)
);
