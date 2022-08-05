import base64
import segno
import io


class QrGenerator():

    def qr_base64(short_url: str) -> base64:
        qr = segno.make(short_url, mask=0)
        bio = io.BytesIO()
        qr.save(bio, kind='png', scale=8, border=0, dark='#3d96e5')
        img_str = base64.b64encode(bio.getvalue())
        return img_str.decode()
