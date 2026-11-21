"""Person matte (white person on black) for a video file with MODNet (ONNX, CPU). Same size/fps as input.
usage: make_matte.py in.mp4 out.mp4 [start_s duration_s] [xmin_frac]   (xmin_frac keeps only people right of that x)"""
import sys, subprocess, json, numpy as np, onnxruntime as ort
from huggingface_hub import hf_hub_download
src, dst = sys.argv[1], sys.argv[2]
ss = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
dd = float(sys.argv[4]) if len(sys.argv) > 4 else None
xmin = float(sys.argv[5]) if len(sys.argv) > 5 else 0.0
info = json.loads(subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate','-of','json',src],capture_output=True,text=True).stdout)['streams'][0]
w, h = info['width'], info['height']; fps = info['r_frame_rate']
sess = ort.InferenceSession(hf_hub_download("Xenova/modnet", "onnx/model.onnx"), providers=["CPUExecutionProvider"])
ih = 512; iw = int(round(w * ih / h / 32)) * 32
args = ['ffmpeg','-v','error','-ss',str(ss),'-i',src] + (['-t',str(dd)] if dd else []) + ['-f','rawvideo','-pix_fmt','rgb24','-']
rd = subprocess.Popen(args, stdout=subprocess.PIPE)
wr = subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','gray','-s',f'{w}x{h}','-r',fps,'-i','-','-c:v','libx264','-crf','14','-pix_fmt','yuv420p',dst], stdin=subprocess.PIPE)
import PIL.Image as Image
n = 0
while True:
    buf = rd.stdout.read(w * h * 3)
    if len(buf) < w * h * 3: break
    im = Image.frombuffer('RGB', (w, h), buf).resize((iw, ih), Image.BILINEAR)
    x = (np.asarray(im, np.float32) / 255.0 - 0.5) / 0.5
    m = sess.run(None, {'input': x.transpose(2, 0, 1)[None]})[0][0, 0]
    m = np.asarray(Image.fromarray((np.clip(m, 0, 1) * 255).astype(np.uint8)).resize((w, h), Image.BILINEAR), np.float32)
    if xmin > 0: m[:, :int(w * xmin)] = 0
    wr.stdin.write(np.clip(m, 0, 255).astype(np.uint8).tobytes()); n += 1
wr.stdin.close(); wr.wait(); print(dst, n, 'frames')
