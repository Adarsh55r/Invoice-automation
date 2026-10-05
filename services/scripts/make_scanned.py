import sys
import fitz

src, dst = sys.argv[1], sys.argv[2]
doc = fitz.open(src)
out = fitz.open()
for page in doc:
    pix = page.get_pixmap(dpi=150)
    new = out.new_page(width=page.rect.width, height=page.rect.height)
    new.insert_image(new.rect, stream=pix.tobytes("png"))
out.save(dst)