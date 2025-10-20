import express from "express";
import path from "path";
import { fileURLToPath } from "url";
import mqtt from "mqtt";
import db from "./db.js";
import bodyParser from "body-parser";

// ===============================
// KONFIGURASI
// ===============================
const MQTT_BROKER = "mqtt://192.168.1.14";
const TOPIC_PUB = "server/esp32";
const TOPIC_SUB = "esp32/server";

let currentMode = "read";
let lastUID = "-";

// tambahkan fitur untuk langsung kosongkan lastUID setelah beberapa request atau detik


// ===============================
// SETUP EXPRESS
// ===============================
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
app.use(express.static(path.join(__dirname, "public")));
app.use(bodyParser.json());

// Endpoint status dashboard
app.get("/status", (req, res) => {
  if (lastUID !== "-") {
    db.query("SELECT * FROM absensi WHERE uid = ?", [lastUID], (err, results) => {
      if (err) return res.json({ success: false, error: err.message });

      let getTime = new Date();

      if (results.length > 0) {
        // UID sudah ada di database
        res.json({
          mode: currentMode,
          uid: lastUID,
          person: results[0], // ambil data orang
          signIn: getTime
        });
      } else {
        // UID belum ada di database
        res.json({
          mode: currentMode,
          uid: lastUID,
          person: null
        });
      }
    });
  } else {
    // Tidak ada UID terakhir
    res.json({ mode: currentMode, uid: lastUID, person: null });
  }
});

// Endpoint ubah mode
app.post("/set-mode/:mode", (req, res) => {
  const mode = req.params.mode;
  currentMode = mode;
  client.publish(TOPIC_PUB, JSON.stringify({ mode }));
  console.log(`🔁 Mode diubah ke: ${mode}`);
  res.json({ success: true, mode });
});

// Endpoint register UID + nama
app.post("/register", (req, res) => {
  const { uid, name } = req.body;
  if (!uid || !name) return res.json({ success: false, error: "UID atau nama kosong" });

  db.query("INSERT IGNORE INTO absensi (uid, name) VALUES (?, ?)", [uid, name], (err) => {
    if (err) return res.json({ success: false, error: err.message });
    lastUID = "-"; // reset UID setelah ditambahkan
    res.json({ success: true });
    console.log(`✅ UID ${uid} berhasil ditambahkan dengan nama ${name}`);
  });
});

const PORT = 3000;
app.listen(PORT, () => console.log(`🌐 Dashboard: http://localhost:${PORT}`));

// ===============================
// KONEKSI MYSQL
// ===============================
db.connect((err) => {
  if (err) console.error("❌ Gagal konek MySQL:", err);
  else console.log("✅ Terhubung ke MySQL");
});

// ===============================
// MQTT CLIENT
// ===============================
const client = mqtt.connect(MQTT_BROKER);

client.on("connect", () => {
  console.log("🚀 Terhubung ke MQTT broker");
  client.subscribe(TOPIC_SUB);
});

client.on("message", (topic, message) => {
  const data = JSON.parse(message.toString());
  console.log("📨 Pesan:", data);

  // ESP Connect
  if (data.type === "esp_connect") {
    client.publish(TOPIC_PUB, JSON.stringify({ mode: currentMode }));
    console.log("🛰️ ESP terhubung, kirim mode awal:", currentMode);
  }

  // UID dari ESP
  if (data.type === "absen" && data.uid) {
    lastUID = data.uid;
    const mode = data.mode || currentMode;

    if (mode === "register") {
      // Jangan langsung simpan, tunggu nama dari dashboard
      console.log(`🔁 Mode REGISTER, UID ${lastUID} menunggu input nama...`);
    } else {
      console.log("📖 UID dibaca:", data.uid);
    }
  }
});
