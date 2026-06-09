import numpy as np
import scipy.signal as signal
import soundfile as sf
import os
import subprocess

def processar_e_renderizar_mp4(diretorio, arquivo_audio, arquivo_imagem, arquivo_video, bass_boost_db=4.0, clarity_boost_db=3.0):
    # Construir os caminhos completos
    input_audio = os.path.join(diretorio, arquivo_audio)
    input_image = os.path.join(diretorio, arquivo_imagem)
    output_video = os.path.join(diretorio, arquivo_video)
    temp_audio = os.path.join(diretorio, "temp_swamp_mastered.wav")

    # Validação de ficheiros
    if not os.path.exists(input_audio):
        print(f"[ERRO] Madié, não encontrei o áudio WAV com o nome:\n--> {arquivo_audio}\nNa pasta: {diretorio}")
        return
        
    if not os.path.exists(input_image):
        print(f"[ERRO] Madié, não encontrei a imagem PNG com o nome:\n--> {arquivo_imagem}\nNa pasta: {diretorio}")
        return

    # -------------------------------------------------------------
    # PASSO 1: MASTERIZAÇÃO DO ÁUDIO
    # -------------------------------------------------------------
    print("\n[*] Passo 1: A dar jarda no áudio (Bass & Clarity)...")
    data, samplerate = sf.read(input_audio)
    nyquist = samplerate / 2
    
    b_low, a_low = signal.butter(4, 120 / nyquist, btype='low')
    b_high, a_high = signal.butter(4, 8000 / nyquist, btype='high')
    
    ganho_bass = 10 ** (bass_boost_db / 20)
    ganho_clarity = 10 ** (clarity_boost_db / 20)
    
    mastered_data = np.zeros_like(data)
    channels = data.shape[1] if len(data.shape) > 1 else 1
    
    for ch in range(channels):
        sinal_original = data[:, ch] if channels > 1 else data
        bass_band = signal.lfilter(b_low, a_low, sinal_original)
        high_band = signal.lfilter(b_high, a_high, sinal_original)
        mid_band = sinal_original - bass_band - high_band
        
        sinal_masterizado = (bass_band * ganho_bass) + mid_band + (high_band * ganho_clarity)
        
        if channels > 1:
            mastered_data[:, ch] = sinal_masterizado
        else:
            mastered_data = sinal_masterizado

    max_peak = np.max(np.abs(mastered_data))
    if max_peak > 0.98:
        mastered_data = (mastered_data / max_peak) * 0.98

    sf.write(temp_audio, mastered_data, samplerate, subtype='FLOAT')
    print("[+] Áudio masterizado guardado temporariamente.")

    # -------------------------------------------------------------
    # PASSO 2: CASAMENTO COM O FFMPEG (CORREÇÃO DE PIXELS PAR)
    # -------------------------------------------------------------
    print(f"\n[*] Passo 2: A forjar o vídeo final [{arquivo_video}] com o FFmpeg...")
    
    ffmpeg_cmd = [
        'ffmpeg', '-y',
        '-loop', '1',
        '-i', input_image,
        '-i', temp_audio,
        '-vf', 'scale=trunc(iw/2)*2:trunc(ih/2)*2', 
        '-c:v', 'libx264',
        '-tune', 'stillimage',
        '-c:a', 'aac',
        '-b:a', '320k',
        '-pix_fmt', 'yuv420p',
        '-shortest',
        output_video
    ]
    
    try:
        subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"\n[+++] PROCESSAMENTO CONCLUÍDO COM SUCESSO! [+++]")
        print(f"--> O teu MP4 está pronto na pasta:\n--> {output_video}")
    except subprocess.CalledProcessError as e:
        print(f"\n[ERRO] O FFmpeg deu o berro:\n{e.stderr.decode('utf-8', errors='ignore')}")
    finally:
        if os.path.exists(temp_audio):
            os.remove(temp_audio)

# =================================================================
# 🎛️ CONSOLE DE CONFIGURAÇÃO DO JOÃO (ALTERA TUDO AQUI EM BAIXO!)
# =================================================================
if __name__ == "__main__":
    
    # 1. O teu caminho do Windows
    pasta_trabalho = r"C:\Users\jmbgo\Imagens pc\MUSICA DIGITAL ORIGINAL"
    
    # 2. ESCRITA DIRETA DOS NOMES (Altera as aspas como quiseres!)
    meu_audio_wav  = "system escapism v2.wav"   # Nome exato do ficheiro que veio do Suno
    minha_capa_png = "system escapism.png"   # Se mudaste o nome do PNG, ajusta aqui!
    meu_video_mp4  = "system escapism v2.mp4"   # O nome que queres para o ficheiro final
    
    # Disparar o motor
    processar_e_renderizar_mp4(
        diretorio=pasta_trabalho,
        arquivo_audio=meu_audio_wav,
        arquivo_imagem=minha_capa_png,
        arquivo_video=meu_video_mp4,
        bass_boost_db=4.0,         
        clarity_boost_db=3.0       
    )