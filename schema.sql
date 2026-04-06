-- ═══════════════════════════════════════════════════════════════════════════
-- CPSMS – Campus Parking Slot Management System
-- MySQL Database Schema (InnoDB)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE DATABASE IF NOT EXISTS cpsms
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE cpsms;

-- ── USERS ───────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    user_id         INT AUTO_INCREMENT PRIMARY KEY,
    user_name       VARCHAR(120)    NOT NULL,
    email           VARCHAR(255)    NOT NULL UNIQUE,
    phone_number    VARCHAR(20)     DEFAULT NULL,
    password_hash   VARCHAR(255)    NOT NULL,
    role            VARCHAR(20)     NOT NULL DEFAULT 'student',
    login_attempts  INT             NOT NULL DEFAULT 0,
    is_locked       TINYINT(1)      NOT NULL DEFAULT 0,

    INDEX idx_users_email (email),
    INDEX idx_users_role  (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── VEHICLES ────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS vehicles (
    vehicle_id      INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT             NOT NULL,
    vehicle_number  VARCHAR(20)     NOT NULL UNIQUE,
    vehicle_type    VARCHAR(30)     NOT NULL,

    INDEX idx_vehicles_user (user_id),
    CONSTRAINT fk_vehicles_user
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── PARKING SLOTS ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS parking_slots (
    slot_id         INT AUTO_INCREMENT PRIMARY KEY,
    slot_location   VARCHAR(100)    NOT NULL,
    slot_status     VARCHAR(20)     NOT NULL DEFAULT 'Available',
    is_active       TINYINT(1)      NOT NULL DEFAULT 1,

    INDEX idx_slots_status  (slot_status),
    INDEX idx_slots_active  (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── RESERVATIONS ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS reservations (
    reservation_id  INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT             NOT NULL,
    vehicle_id      INT             NOT NULL,
    slot_id         INT             NOT NULL,
    reservation_date DATE           NOT NULL,
    reservation_time TIME           NOT NULL,
    is_active       TINYINT(1)      NOT NULL DEFAULT 1,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_reservations_user (user_id),
    INDEX idx_reservations_slot (slot_id),
    INDEX idx_reservations_active (is_active),

    CONSTRAINT fk_reservations_user
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON UPDATE CASCADE,
    CONSTRAINT fk_reservations_vehicle
        FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id)
        ON UPDATE CASCADE,
    CONSTRAINT fk_reservations_slot
        FOREIGN KEY (slot_id) REFERENCES parking_slots(slot_id)
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── REPORTS ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS reports (
    report_id       INT AUTO_INCREMENT PRIMARY KEY,
    admin_id        INT             NOT NULL,
    report_date     DATE            NOT NULL,
    report_type     VARCHAR(50)     NOT NULL,

    CONSTRAINT fk_reports_admin
        FOREIGN KEY (admin_id) REFERENCES users(user_id)
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
