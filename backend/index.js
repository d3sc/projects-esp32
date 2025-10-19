import express from "express";
import path from "path";
import { fileURLToPath } from "url";
import mqtt from "mqtt";
import db from "./db.js";
import readline from "readline";

// ===============================
// KONFIGURASI
// ===============================
const MQTT_BROKER = "mqtt://192.168.1.14";
const TOPIC_PUB = "server/esp32";
const TOPIC_SUB = "esp32/server";
let currentMode = "read";
let lastUID = "-";

// ===============================
// SETUP EXPRESS
// ===============================
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
app.use(express.static(path.join(__dirname, "public")));

app.get("/status", (req, res) => {
  res.json({ mode: currentMode, uid: lastUID });
});

app.post("/set-mode/:mode", (req, res) => {
  const mode = req.params.mode;
  currentMode = mode;
  client.publish(TOPIC_PUB, JSON.stringify({ mode }));
  console.log(`🔁 Mode diubah ke: ${mode}`);
  res.json({ success: true, mode });
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
      db.query("INSERT IGNORE INTO absensi (uid) VALUES (?)", [data.uid], (err) => {
        if (err) console.error("❌ Gagal simpan UID:", err);
        else console.log("✅ UID terdaftar:", data.uid);
      });
    } else {
      console.log("📖 UID dibaca:", data.uid);
    }
  }
});
