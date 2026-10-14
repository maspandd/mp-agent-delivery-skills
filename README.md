# pandu-agent-skills

Kumpulan skill yang bisa dipakai ulang di Claude.ai, Claude Code, dan agent lain (Codex, Cursor, GitHub Copilot, Gemini CLI).

Setiap skill mengikuti standar terbuka Agent Skills: satu folder berisi `SKILL.md`. Spesifikasi: https://agentskills.io/specification

## Isi

| Skill | Fungsi | Kebutuhan |
|---|---|---|
| `estimate-delivery-plan` | Mengubah estimasi sprint menjadi delivery plan di Google Sheet: review estimasi, skenario tim, pros/cons, timeline modul, kalender dengan hari libur. | Akses baca/tulis Google Sheets (connector Claude atau MCP server Google Sheets). |

## Struktur repo

```
.claude-plugin/marketplace.json   Katalog plugin untuk Claude Code
skills/<nama-skill>/SKILL.md      Skill (format Agent Skills)
scripts/validate.py               Cek SKILL.md terhadap spesifikasi
scripts/package.sh                Buat ZIP per skill di dist/ untuk upload ke Claude.ai
.github/workflows/validate.yml    Validasi tiap push; lampirkan ZIP ke release tiap tag v*
```

Ganti `OWNER` di bawah dengan username GitHub Anda.

## Pasang di Claude.ai (web, desktop, mobile)

1. Unduh `estimate-delivery-plan.zip` dari halaman Releases. Atau jalankan `bash scripts/package.sh`.
2. Buka Settings > Capabilities. Pastikan "Code execution and file creation" aktif.
3. Di bagian Skills, klik "Upload skill". Pilih ZIP tersebut.

Skill yang di-upload manual tidak ikut update dari GitHub. Upload ZIP baru setiap kali skill berubah.

Alternatif untuk plan Team atau Enterprise: Owner organisasi bisa sync repo ini lewat Organization settings > Plugins & skills. Repo harus private. Skill lalu tersedia untuk semua anggota dan mengikuti isi repo.

## Pasang di Claude Code

```bash
claude plugin marketplace add OWNER/pandu-agent-skills
claude plugin install pandu-skills@pandu-agent-skills
```

Panggil dengan `/pandu-skills:estimate-delivery-plan`. Claude juga memakainya otomatis jika permintaan cocok dengan `description`.

Auto-update mati secara default. Ambil update manual:

```bash
claude plugin marketplace update pandu-agent-skills
claude plugin update pandu-skills@pandu-agent-skills
```

Atau nyalakan auto-update: `/plugin` > Marketplaces > pilih `pandu-agent-skills` > Enable auto-update.

Ingin nama tanpa prefix (`/estimate-delivery-plan`)? Salin folder skill ke `~/.claude/skills/estimate-delivery-plan/`. Cara ini tidak dapat update otomatis.

## Pasang di agent lain

Pakai CLI `skills` (https://github.com/vercel-labs/skills). CLI ini menyalin skill ke folder yang dibaca tiap agent.

```bash
npx skills add OWNER/pandu-agent-skills --skill estimate-delivery-plan \
  -a codex -a cursor -a github-copilot -a gemini-cli -g
```

Tanpa `-g`, skill dipasang di project saat ini, bukan di home.

Pasang manual: salin folder `skills/estimate-delivery-plan/` ke folder skill agent.

| Agent | Folder project | Folder global |
|---|---|---|
| Claude Code | `.claude/skills/` | `~/.claude/skills/` |
| Codex | `.agents/skills/` | `~/.agents/skills/` |
| Cursor | `.agents/skills/` | `~/.cursor/skills/` |
| GitHub Copilot | `.agents/skills/` | `~/.copilot/skills/` |
| Gemini CLI | `.agents/skills/` | `~/.gemini/skills/` |

Sumber tabel: README `vercel-labs/skills`. Cek ulang jika agent tidak menemukan skill.

Agent lain butuh tool Google Sheets sendiri (MCP server atau API client). Tanpa tool itu, skill berhenti dan memberi tahu user.

## Repo private

- Claude Code memakai kredensial git Anda (SSH atau credential helper).
- CLI `skills` mencoba credential helper git, lalu `gh`, lalu SSH. `GITHUB_TOKEN` atau `GH_TOKEN` juga diterima.

## Ubah atau tambah skill

1. Edit `skills/<nama>/SKILL.md`. Untuk skill baru, buat folder baru. Nama folder harus sama dengan field `name`.
2. Naikkan `metadata.version` di SKILL.md sebagai catatan. `marketplace.json` sengaja tidak punya `version`, jadi Claude Code mengikuti commit terbaru. Jika Anda menambah `version`, Anda wajib menaikkannya di setiap rilis; tanpa itu user tidak menerima perubahan.
3. Jalankan `python3 scripts/validate.py .` (butuh `pip install pyyaml`).
4. Commit dan push. Untuk rilis ZIP: `git tag v1.0.1 && git push --tags`.

Aturan `name`: huruf kecil, angka, dan tanda hubung. Maksimal 64 karakter. `description` maksimal 1024 karakter. `SKILL.md` sebaiknya di bawah 500 baris; pindahkan detail ke `references/`.
