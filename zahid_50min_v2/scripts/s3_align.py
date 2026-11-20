"""Script 3: align script sentences to audio pauses (DP) -> timeline.json, plus audio envelope for lip-sync."""
import json, re, subprocess, math
import numpy as np

FF = "/tmp/vid/ffmpeg"; AUD = "/tmp/vid/audio_repo/audio01.mp3"; OUT = "/tmp/vid/out/"

SCRIPT = [
 ("hook", ["একটা ফোনের স্ক্রিন বদলাতে পঞ্চাশ মিনিট।", "এই একটা লাইনই একসময় জাহিদের দোকানের ভাগ্য বদলে দিয়েছিল।"]),
 ("rent", ["অথচ এক বছর আগে এই দোকানের ভাড়া দিতে না পেরে সে শাটার বন্ধ করে দেওয়ার কথা ভাবছিল।"]),
 ("street", ["মিরপুরের ছোট একটা মোবাইল সার্ভিসিং দোকান।"]),
 ("inside", ["বাবার রেখে যাওয়া শেষ সম্পদ।", "দেয়ালে একটা পুরনো ঘড়ি।"]),
 ("busy", ["দোকানটা বাঁচাতে জাহিদ কত কিছুই করেছে, শুধু একটা জিনিস কখনো করেনি।", "নিজের কাজের সময় মেপে দেখেনি।"]),
 ("ad", ["তার বিজ্ঞাপনে লেখা ছিল, “দ্রুত ও নির্ভরযোগ্য মোবাইল সার্ভিস।”", "কিন্তু দ্রুত মানে কত দ্রুত?"]),
 ("counter", ["প্রতিদিন লোক আসত।", "ফোন দেখিয়ে জিজ্ঞেস করত, “ভাই, কতক্ষণ লাগবে?”", "জাহিদ বলত, “হয়ে যাবে।”",
              "লোকটা আবার জিজ্ঞেস করত, “কখন?”", "জাহিদ কোনো নির্দিষ্ট উত্তর দিতে পারত না।",
              "কিছুক্ষণ পর লোকটা ফোন নিয়ে পাশের বড় দোকানে চলে যেত।"]),
 ("girl1", ["একদিন একটা স্কুলপড়ুয়া মেয়ে এল।", "পরদিন তার পরীক্ষা।", "সব পড়া ফোনে।", "স্ক্রিনটা ভাঙা।"]),
 ("girl2", ["মেয়েটা জিজ্ঞেস করল, “ভাইয়া, আজ রাতের মধ্যে পাব?”", "জাহিদ বলল, “হয়ে যাবে।”",
            "মেয়েটা কিছুক্ষণ চুপ করে থেকে বলল, “হয়ে যাবে মানে কখন? আমি অপেক্ষা করব, নাকি অন্য দোকানে যাব?”"]),
 ("realize", ["কথাটা খুব সাধারণ।", "কিন্তু জাহিদের কাছে সেদিন প্রথমবার মনে হলো, মানুষ শুধু ফোন ঠিক করাতে আসে না।",
              "তারা জানতে চায়, ফোনটা কখন ফিরে পাবে।"]),
 ("night", ["সেদিন রাতে দোকান বন্ধ করার পর জাহিদ প্রথমবার দেয়ালের ঘড়িটার দিকে তাকাল।", "তারপর দশটা ফোনের স্ক্রিন বদল করল।",
            "প্রতিটার শুরুর সময় আর শেষের সময় খাতায় লিখল।", "দেখল, সাধারণ মডেলের স্ক্রিন বদলাতে সবচেয়ে বেশি সময় লেগেছে পঞ্চাশ মিনিট।",
            "সবচেয়ে কম চল্লিশ।"]),
 ("sign", ["পরদিন সকালে বিজ্ঞাপনের পুরনো লাইনটা কেটে দিল।", "নতুন করে লিখল:",
           "“সাধারণ মডেলের স্ক্রিন বদলান ৫০ মিনিটে। না পারলে চার্জ অর্ধেক।”"]),
 ("six", ["প্রথম দিন ছয়জন কাস্টমার এল।", "এবার কেউ শুধু দাম জিজ্ঞেস করল না।", "তারা ঘড়ির দিকে তাকিয়ে অপেক্ষা করল।"]),
 ("rare", ["কিন্তু আসল পরীক্ষাটা এল তৃতীয় সপ্তাহে।", "একজন কাস্টমার নিয়ে এলেন একটা বিরল মডেলের ফোন।",
           "কাজ করতে সত্তর মিনিট লাগল।", "জাহিদ ফোনটা হাতে দিয়ে বলল, “ভাই, আমার কথা রাখতে পারিনি। তাই শ্রমের চার্জ অর্ধেক দিন।”"]),
 ("brother", ["লোকটা অবাক হয়ে বললেন, “আপনি নিজে থেকেই কমাচ্ছেন?”", "জাহিদ শুধু মাথা নাড়ল।",
              "পরের সপ্তাহে সেই লোক নিজের ভাইকে নিয়ে এলেন।"]),
 ("promise", ["ধীরে ধীরে জাহিদ বুঝল, শুধু দ্রুত কাজ করলেই হয় না।", "নিজের প্রতিশ্রুতির দায়িত্বও নিতে হয়।"]),
 ("book", ["জন ক্যাপলসের বই Tested Advertising Methods-এ বিজ্ঞাপনের একটা গুরুত্বপূর্ণ শিক্ষা আছে।"]),
 ("claims", ["সহজ কথায়, “ভালো”, “সেরা”, “দ্রুত” এগুলো শুধু দাবি।",
             "কিন্তু নির্দিষ্ট সংখ্যা মানুষকে বোঝায়, আপনি আসলে কী দিতে পারবেন।"]),
 ("takeaway", ["আমার practical takeaway:",
               "পরের বার বিজ্ঞাপন লেখার আগে নিজেকে জিজ্ঞেস করো, আমার কথাটা কি কেউ ঘড়ি ধরে মিলিয়ে দেখতে পারবে?"]),
 ("ending", ["জাহিদের দোকানের ঘড়িটা এখনও দেয়ালে।", "পার্থক্য শুধু একটাই, এখন সে আর ঘড়িটাকে এড়িয়ে চলে না।"]),
 ("final", ["কারণ “দ্রুত” একটা দাবি।", "আর “পঞ্চাশ মিনিট” একটা প্রতিশ্রুতি।", "এমন আরও practical গল্পের জন্য follow করুন।"]),
]

def syl(txt):
    n = 0.0; ch = list(txt)
    for i, c in enumerate(ch):
        o = ord(c)
        if 0x0985 <= o <= 0x0994 or 0x0995 <= o <= 0x09B9 or o in (0x09DC, 0x09DD, 0x09DF, 0x09CE):
            if i + 1 < len(ch) and ch[i + 1] == "\u09cd": continue
            n += 1
        elif 0x09E6 <= o <= 0x09EF or c.isdigit():
            n += 1.5
    for w in re.findall(r"[A-Za-z]+", txt):
        n += max(1, len(re.findall(r"[aeiouy]+", w.lower())))
    return n

# Sentence start times (= speech resumes after the pause), verified against the silence map and two Whisper passes.
# NOTE: audio01.mp3 ends (124.37s) in the middle of the story, right after the "rare model phone" sentence,
# so only the sentences that are really narrated are on the timeline.
STARTS = {
 "hook": [0.0, 3.77], "rent": [7.82], "street": [14.01], "inside": [16.69, 18.91], "busy": [20.92, 25.76],
 "ad": [28.06, 32.26], "counter": [34.86, 36.31, 39.66, 41.88, 44.49, 47.02], "girl1": [51.34, 53.40, 54.78, 56.04],
 "girl2": [57.49, 61.41, 64.07], "realize": [71.41, 72.92, 77.90], "night": [81.18, 86.22, 88.96, 92.49, 97.92],
 "sign": [100.34, 103.25, 104.60], "six": [109.91, 111.94, 114.24], "rare": [117.20, 119.94, 123.34],
}

def main():
    sj = json.load(open(OUT + "silences.json")); dur = sj["duration"]; sil = sj["silences"]
    flat = [(name, st, tx) for (name, chunks) in SCRIPT if name in STARTS
            for st, tx in zip(STARTS[name], chunks)]
    scenes, order = [], []
    for name, _ in SCRIPT:
        if name in STARTS: order.append(name)
    for si, name in enumerate(order):
        cl = [(st, tx) for (n, st, tx) in flat if n == name]
        s0 = cl[0][1] if False else cl[0][0]
        nxt_start = STARTS[order[si + 1]][0] if si + 1 < len(order) else dur
        chunks = []
        for k, (st, tx) in enumerate(cl):
            en = cl[k + 1][0] if k + 1 < len(cl) else nxt_start
            chunks.append({"text": tx, "start": round(st, 3), "end": round(en, 3), "syl": syl(tx)})
        scenes.append({"name": name, "start": chunks[0]["start"], "end": round(nxt_start, 3), "chunks": chunks})
    json.dump({"duration": dur, "scenes": scenes, "silences": sil}, open(OUT + "timeline.json", "w"), ensure_ascii=False, indent=1)
    for s in scenes:
        print(f"== {s['name']:9s} {s['start']:7.2f} - {s['end']:7.2f}  ({s['end'] - s['start']:.1f}s)")
    raw = subprocess.run([FF, "-v", "quiet", "-i", AUD, "-f", "s16le", "-ac", "1", "-ar", "16000", "-"], capture_output=True).stdout
    a = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768
    hop = 16000 // 60; n = len(a) // hop
    env = np.sqrt((a[: n * hop].reshape(n, hop) ** 2).mean(1))
    env = env / np.percentile(env, 95)
    np.save(OUT + "env.npy", np.clip(env, 0, 1.2))

main()
