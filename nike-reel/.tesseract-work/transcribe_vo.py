import json, sys, time, subprocess
import numpy as np
from faster_whisper import WhisperModel
src = sys.argv[1]; out = sys.argv[2]
prompt = ("Well, turns out, Nike needed retail more than anyone. That was 2021. Nike was soaring at almost 280 billion dollars. "
          "It even got kicked out of the S&P 100. In 2020, Nike hired eBay's ex-CEO, John Donahoe. Nike pulled out of stores like DSW and Dillard's, "
          "and sent less to Foot Locker. Hoka and On. Alo and Vuori became the new flex. Dunks. Air Force 1s. Retro Jordans. Elliott Hill. Tariffs.")
t0 = time.time()
m = WhisperModel("medium.en", device="cpu", compute_type="int8", cpu_threads=4)
audio = np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",src,"-ac","1","-ar","16000","-f","f32le","-"],capture_output=True).stdout, np.float32)
segs, info = m.transcribe(audio, language="en", word_timestamps=True, initial_prompt=prompt, beam_size=5, vad_filter=False, condition_on_previous_text=False)
words = []
for s in segs:
    for w in s.words:
        words.append({"w": w.word.strip(), "s": round(w.start, 3), "e": round(w.end, 3), "p": round(w.probability, 3)})
json.dump({"model": "faster-whisper medium.en int8", "source": src, "words": words}, open(out, "w"), indent=1)
print(len(words), "words in", round(time.time() - t0, 1), "s")
print(" ".join(w["w"] for w in words))
