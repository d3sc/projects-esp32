import mysql from "mysql2";

const db = mysql.createConnection({
  host: "localhost",
  user: "root",       // ubah sesuai user MySQL kamu
  password: "",       // ubah juga kalau pakai password
  database: "absensi_esp32"
});

db.connect((err) => {
  if (err) {
    console.error("❌ Gagal konek database:", err);
  } else {
    console.log("✅ Terhubung ke database MySQL");
  }
});

export default db;
