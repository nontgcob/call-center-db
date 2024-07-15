CREATE TABLE "callers" (
    "id" INTEGER,
    "name" TEXT,
    "job_title" TEXT,
    "department" TEXT,
    PRIMARY KEY("id")
);

CREATE TABLE "calls" (
    "id" INTEGER AUTO_INCREMENT,
    "caller_id" INTEGER,
    "operator_id" INTEGER,
    "problem_id" INTEGER,
    "reason" TEXT,
    "date_time" DATETIME,
    PRIMARY KEY("id"),
    FOREIGN KEY("caller_id") REFERENCES "callers"("id"),
    FOREIGN KEY("operator_id") REFERENCES "operators"("id"),
    FOREIGN KEY("problem_id") REFERENCES "problems"("id")
);

CREATE TABLE "operators" (
    "id" INTEGER,
    "name" TEXT,
    "password" TEXT,
    PRIMARY KEY("id")
);

CREATE TABLE "problems" (
    "id" INTEGER AUTO_INCREMENT,
    "description" TEXT,
    "problem_type_id" TEXT,
    "device_serial_number" INTEGER,
    "specialist_id" INTEGER,
    "resolved_date_time" DATETIME,
    "resolved_solution" TEXT,
    "resolved_time_taken" INTEGER,
    "date_time" DATETIME,
    PRIMARY KEY("id"),
    FOREIGN KEY("problem_type_id") REFERENCES "problem_types"("id"),
    FOREIGN KEY("device_serial_number") REFERENCES "devices"("serial_number"),
    FOREIGN KEY("specialist_id") REFERENCES "specialists"("id")
);

CREATE TABLE "problem_types" (
    "id" INTEGER,
    "problem_type" TEXT,
    PRIMARY KEY("id")
);

CREATE TABLE "devices" (
    "serial_number" INTEGER,
    "device" TEXT,
    "type" TEXT,
    PRIMARY KEY("serial_number")
);

CREATE TABLE "mapping_problems_softwares" (
    "id" INTEGER,
    "problem_id" INTEGER,
    "software_product_key" INTEGER,
    PRIMARY KEY("id"),
    FOREIGN KEY("problem_id") REFERENCES "problems"("id"),
    FOREIGN KEY("software_product_key") REFERENCES "softwares"("product_key")
);

CREATE TABLE "softwares" (
    "product_key" INTEGER,
    "software" TEXT,
    "valid_license" DATETIME,
    PRIMARY KEY("product_key")
);

CREATE TABLE "specialties" (
    "id" INTEGER,
    "problem_type_id" INTEGER,
    "specialist_id" INTEGER,
    PRIMARY KEY("id"),
    FOREIGN KEY("problem_type_id") REFERENCES "problem_types"("id"),
    FOREIGN KEY("specialist_id") REFERENCES "specialists"("id")
);

CREATE TABLE "specialists" (
    "id" INTEGER,
    "name" TEXT,
    "workload" INTEGER,
    PRIMARY KEY("id")
);