from elink.settings import BASE_DIR
import base64
import io
import segno

# Тут делаем QR код и возвращаем его в виде base64
class QrGenerator():

    def qr_base64(short_url: str) -> base64:
        
        #qr = qrcode.make(short_url)
        qr = segno.make(short_url, mask=0)
        bio = io.BytesIO()
        #qrcode.make_image(back_color=(255, 195, 235), fill_color=(55, 95, 35))
        #qr.save('henry-lee.png')
        qr.save(bio, kind='png', scale=8, border=0, dark='#3d96e5')
        #qr.to_artistic(background=f'{BASE_DIR}/back.png', target=bio, kind='png', scale=6, border=0, dark='#3d96e5')
        
        img_str = base64.b64encode(bio.getvalue())
        #print(base64(bio.getvalue()))
        #print(img_str.decode())
        return img_str.decode()
