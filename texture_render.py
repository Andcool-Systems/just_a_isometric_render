from PIL import Image, ImageEnhance
import pygame

class Texture:
    def __init__(self, filename: [str, str, str], resolution: int, koef: float = 0.8) -> None:
        raw_left = Image.open(filename[0]).convert("RGBA")
        raw_left = raw_left.resize((resolution, resolution), resample=Image.Resampling.NEAREST)
        self.left = self.to_pg(raw_left)

        raw_right = Image.open(filename[1]).convert("RGBA")
        raw_right = raw_right.resize((resolution, resolution), resample=Image.Resampling.NEAREST)
        self.right = self.to_pg(raw_right)

        raw_top = Image.open(filename[2]).convert("RGBA")
        raw_top = raw_top.resize((resolution, resolution), resample=Image.Resampling.NEAREST)
        self.top = self.to_pg(raw_top)

        img_r = raw_right.transform((raw_right.size[0] * 2, raw_right.size[1] * 2), Image.Transform.AFFINE, (1, 0, 0, 0.5, 1, -(raw_right.size[1] // 2), 0, 0), resample=Image.Resampling.BICUBIC)
        enhancer = ImageEnhance.Brightness(img_r)
        factor = koef - 0.2
        img_r = enhancer.enhance(factor)

        img_l = raw_left.transform((raw_left.size[0] * 2, raw_left.size[1] * 2), Image.Transform.AFFINE, (1, 0, 0, -0.5, 1, -(raw_left.size[1] // 2), 0, 0), resample=Image.Resampling.BICUBIC)
        enhancer = ImageEnhance.Brightness(img_l)
        factor = 0.7
        img_l = enhancer.enhance(factor)

        img_top = raw_top.rotate(45, expand=True)
        img_top = img_top.transform((img_top.size[0], img_top.size[1]), Image.Transform.AFFINE, (1, 0, 0, 0, 2, 0, 0, 0), resample=Image.Resampling.BICUBIC)
        koef = ((img_l.size[0] // 2) + (img_r.size[0] // 2)) / img_top.size[0]
        img_top = img_top.resize((int(img_top.size[0] * koef), int(img_top.size[1] * koef)))

        base = Image.new("RGBA", ((img_l.size[0] // 2) + (img_r.size[0] // 2), (img_top.size[1] // 2) + (img_l.size[1] // 2)), (0, 0, 0, 0))
        final_pos_y = img_top.size[1] // 4
        base.paste(img_l, (0, final_pos_y - img_l.size[1] // 4), img_l)
        base.paste(img_r, (img_r.size[0] // 2, final_pos_y), img_r)
        base.paste(img_top, (0, final_pos_y - (img_top.size[1] // 4) + 1), img_top)

        self.texture = self.to_pg(base)
    
    def to_pg(self, image: Image) -> pygame.Surface:
        mode = image.mode 
        size = image.size 
        data = image.tobytes() 
        
        # Convert PIL image to pygame surface image 
        return pygame.image.fromstring(data, size, mode) 

