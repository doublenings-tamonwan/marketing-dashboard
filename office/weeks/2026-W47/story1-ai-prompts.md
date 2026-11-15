# คำสั่งสร้างภาพ AI ฉากหลัง — ซีรีส์ไม่ได้บอก EP.1 "ทำไมในซีรีส์เกาหลี วันเกิดต้องกินซุปสาหร่าย?"

> ต้องเปิดป้ายเนื้อหาสร้างด้วย AI ตอนโพสต์ (TikTok: "AI-generated content")

ฉากหลังเป็นภาพสมจริง + น้องนางาจิ (สติกเกอร์ขอบขาว) ยืนเล่าด้านล่างกลางจอ
**ต้องสร้างทั้งหมด 7 ภาพ** (ฉาก 8 และ 9 ใช้ภาพซ้ำ)

## ภาพไหนใช้ฉากไหน

| เลขภาพ | ใช้ในฉาก | ภาพนี้คืออะไร |
|---|---|---|
| bg1 | ฉาก 1 (0–3 วิ ฮุก) + ฉาก 9 (47–55 วิ ชวนเมนต์) | โต๊ะอาหารเช้าวันเกิด ชามซุปสาหร่ายควันกรุ่นตรงกลาง |
| bg2 | ฉาก 2 (3–6 วิ "กินวันสอบ…สอบตก!?") | โต๊ะอ่านหนังสือตอนกลางคืน กระดาษข้อสอบ ดินสอ โคมไฟ |
| bg3 | ฉาก 3 (6–11 วิ ชื่อ "มิยอกกุก") + ฉาก 8 (40–47 วิ สำนวน "กินซุปสาหร่าย = สอบตก") | ชามซุปสาหร่ายใกล้ ๆ เห็นสาหร่ายในน้ำซุปชัด |
| bg4 | ฉาก 4 (11–18 วิ อาหารแม่หลังคลอด) | มือแม่ถือชามซุปข้างเปลเด็ก ไม่เห็นหน้า |
| bg5 | ฉาก 5 (18–25 วิ วันเกิด = ระลึกถึงแม่) | มือแม่วางชามซุปลงตรงหน้ามือลูกที่โตแล้ว (ไม่เห็นหน้า) |
| bg6 | ฉาก 6 (25–33 วิ เรื่องเล่าสมัยโชซอน) | **ภาพวาดสีน้ำแบบเกาหลีโบราณ** วาฬกับสาหร่ายในทะเล |
| bg7 | ฉาก 7 (33–40 วิ "ลื่น = สอบตก") | ตะเกียบคีบสาหร่ายลื่น ๆ หยดน้ำซุป |

ทำไมเลือกซ้ำแบบนี้:
- ฉาก 8 พูดถึงสำนวน "กินซุปสาหร่าย" → ใช้ภาพชามซุปใกล้ ๆ (bg3) แต่ให้ตอนตัดต่อ **ซูมเข้าช้า ๆ อีกมุม** จะไม่รู้สึกว่าภาพซ้ำ
- ฉาก 9 ปิดคลิป → กลับมาภาพโต๊ะวันเกิด (bg1) เหมือนปิดวงกลมกับฮุก ใส่ปุ่ม "กดติดตาม" ทับได้เลย

---

## วิธีใช้ (สำหรับเจ้าของช่อง)

1. เปิดแอป **Gemini** หรือ **ChatGPT** (ฟรีได้ทั้งคู่)
2. กดปุ่มคัดลอกที่มุมกล่องคำสั่งด้านล่าง → วางในช่องแชท → ส่ง
3. ถ้าภาพออกมาเป็น **สี่เหลี่ยมจัตุรัสหรือแนวนอน** ให้พิมพ์ต่อว่า `make it vertical 9:16`
4. ถ้าภาพมีตัวหนังสือ หน้าคน หรือดูแปลก ๆ ให้พิมพ์ประโยคในบรรทัด "ถ้าภาพออกมาไม่ดี ลองเติม" ต่อได้เลย
5. ทำทีละภาพ **ในแชทเดียวกันต่อเนื่อง** (สีจะออกมาคุมกันมากกว่าเปิดแชทใหม่)
6. บันทึกภาพ ตั้งชื่อ `bg1.png`, `bg2.png` … `bg7.png` แล้วส่งมาในแชทได้เลย

ไม่ต้องห่วงว่าด้านบน/ด้านล่างของภาพจะดูโล่ง ๆ เบลอ ๆ — ตั้งใจเว้นไว้วางป้ายข้อความและน้องนางาจิ

---

## คำสั่งรายภาพ

ทุกคำสั่งมีท้ายเหมือนกัน (สไตล์ + การจัดวาง) เพื่อให้ทั้งคลิปสีคุมกัน ไม่ต้องแก้

### bg1 — โต๊ะวันเกิด ชามซุปสาหร่าย (ฉาก 1, 9)

```
Vertical 9:16 photorealistic photo of a cozy Korean home breakfast table on a birthday morning. A white ceramic bowl of steaming Korean seaweed soup (miyeokguk, dark green seaweed in clear brown broth) sits in the center, surrounded by a bowl of white rice, a few small side dishes (kimchi, spinach namul), metal chopsticks and a long Korean spoon on a wooden table, a tiny vase of small flowers in the background. Soft rising steam catches the light. Main subject placed in the middle-upper part of the frame. The top 15% of the image is soft out-of-focus dark background, and the bottom 45% is an empty, blurred, softly lit wooden tabletop with nothing on it. Warm cinematic lighting, deep navy blue shadows with warm butter-yellow highlights, shallow depth of field, rich contrast, eye-catching, high detail. No people, no text, no letters, no logo, no watermark.
```
คำอธิบาย: โต๊ะอาหารเช้าบ้านเกาหลี ชามซุปสาหร่ายควันกรุ่นเป็นพระเอก มีข้าว เครื่องเคียง ไม่มีคน
ถ้าภาพออกมาไม่ดี ลองเติม: `make the soup bowl bigger and closer, leave the bottom half of the image as empty blurred table, remove any text`

### bg2 — โต๊ะอ่านหนังสือสอบ (ฉาก 2)

```
Vertical 9:16 photorealistic photo of a student's study desk late at night before a big exam. A blank exam answer sheet with empty multiple-choice bubbles, a sharpened pencil, an eraser and a stack of closed textbooks, lit by a single warm desk lamp. Slight tense mood. Main subject placed in the middle-upper part of the frame. The top 15% of the image is soft out-of-focus dark background, and the bottom 45% is an empty, blurred, dimly lit desk surface. Warm cinematic lighting, deep navy blue shadows with warm butter-yellow highlights from the lamp, shallow depth of field, rich contrast, eye-catching, high detail. No people, no faces, no readable text, no letters, no numbers, no logo, no watermark.
```
คำอธิบาย: โต๊ะอ่านหนังสือคืนก่อนสอบ กระดาษคำตอบเปล่า ดินสอ โคมไฟแสงอุ่น (ไม่มีตัวหนังสืออ่านออก)
ถ้าภาพออกมาไม่ดี ลองเติม: `make all paper and book covers completely blank with no writing at all`

### bg3 — ซุปสาหร่ายใกล้ ๆ (ฉาก 3, 8)

```
Vertical 9:16 photorealistic close-up food photo of Korean seaweed soup (miyeokguk) in a white ceramic bowl, seen from a 45-degree angle. Silky dark green seaweed ribbons floating in a clear light-brown broth with a few small pieces of beef, glistening sesame oil droplets on the surface, gentle steam rising. A Korean metal spoon rests beside the bowl. Main subject placed in the middle-upper part of the frame. The top 15% of the image is soft out-of-focus dark background, and the bottom 45% is an empty, blurred, softly lit dark wooden table. Warm cinematic lighting, deep navy blue shadows with warm butter-yellow highlights, shallow depth of field, rich contrast, appetizing, eye-catching, high detail. No people, no text, no letters, no logo, no watermark.
```
คำอธิบาย: ชามซุปสาหร่ายระยะใกล้ เห็นสาหร่ายเส้นนุ่ม ๆ น้ำซุปใส ควันกรุ่น ให้คนดูรู้จักหน้าตาเมนู
ถ้าภาพออกมาไม่ดี ลองเติม: `show the seaweed more clearly, more steam, keep the bottom half empty and blurred`

### bg4 — มือแม่หลังคลอดถือชามซุปข้างเปล (ฉาก 4)

```
Vertical 9:16 photorealistic photo inside a quiet, warm Korean home bedroom. Close-up of a new mother's hands, wearing a soft cream cardigan sleeve, gently holding a white bowl of steaming seaweed soup, next to a wooden baby crib with a soft white blanket; a newborn's tiny hand is just visible resting on the blanket. Only hands are visible, the mother's face is completely out of frame. Calm, tender, peaceful mood. Main subject placed in the middle-upper part of the frame. The top 15% of the image is soft out-of-focus dark background, and the bottom 45% is an empty, blurred, softly lit blanket and floor area. Warm cinematic lighting, deep navy blue shadows with warm butter-yellow window light, shallow depth of field, rich contrast, eye-catching, high detail. No faces, no text, no letters, no logo, no watermark, no medical equipment.
```
คำอธิบาย: มือแม่ถือชามซุปข้างเปลเด็ก เห็นมือเล็ก ๆ ของทารกนิดเดียว ไม่เห็นหน้าใคร บรรยากาศอบอุ่นสงบ (ไม่มีของทางการแพทย์ ไม่สื่อว่าซุปรักษาโรค)
ถ้าภาพออกมาไม่ดี ลองเติม: `crop so that no face is visible at all, only hands, bowl and crib`

### bg5 — มือแม่วางชามซุปให้ลูกที่โตแล้ว (ฉาก 5)

```
Vertical 9:16 photorealistic photo of a heartwarming birthday moment at a Korean dining table. An older mother's hands gently place a white bowl of steaming seaweed soup in front of her grown-up child's hands, which rest on the wooden table. Only hands and forearms are visible, no faces in the frame. A small birthday cake with one lit candle glows softly out of focus in the background. Emotional, grateful, tender mood. Main subject placed in the middle-upper part of the frame. The top 15% of the image is soft out-of-focus dark background with warm bokeh lights, and the bottom 45% is an empty, blurred, softly lit wooden tabletop. Warm cinematic lighting, deep navy blue shadows with warm butter-yellow candle-like highlights, shallow depth of field, rich contrast, eye-catching, high detail. No faces, no text, no letters, no logo, no watermark.
```
คำอธิบาย: มือแม่ (วัยกลางคน) วางชามซุปให้มือลูกที่โตแล้ว เค้กเทียนเล่มเดียวเบลอ ๆ ข้างหลัง สื่อ "วันเกิด = ระลึกถึงแม่" จุดซึ้งของคลิป
ถ้าภาพออกมาไม่ดี ลองเติม: `only show hands, no faces, make the mood warmer and more emotional`

### bg6 — เรื่องเล่าวาฬ ภาพวาดเกาหลีโบราณ (ฉาก 6)

```
Vertical 9:16 semi-realistic traditional Korean painting in the style of a Joseon-era ink and watercolor folk painting on aged hanji paper. A large mother whale swimming gracefully under the sea with her newborn calf beside her, surrounded by long flowing ribbons of dark green seaweed swaying in the water, stylized waves drawn with fine ink lines at the top. Mythical storybook feeling, like an old legend. Main subject placed in the middle-upper part of the frame. The top 15% of the image is soft empty washed paper-and-water texture, and the bottom 45% is calm, empty, softly blurred deep-water wash with no objects. Muted palette of deep navy blue ink with warm butter-yellow and soft gold paper tones, gentle texture, rich depth, eye-catching. No people, no text, no Korean or Chinese characters, no calligraphy, no red seal stamps, no logo, no watermark.
```
คำอธิบาย: ภาพวาดสีน้ำแบบเกาหลีสมัยโชซอนบนกระดาษเก่า แม่วาฬกับลูกว่ายท่ามกลางสาหร่าย ตั้งใจให้ดูเป็น "ตำนาน/เรื่องเล่า" ไม่ใช่ภาพจริง (ตรงกับผลตรวจที่ให้เล่าเป็นเรื่องเล่าเท่านั้น)
ถ้าภาพออกมาไม่ดี ลองเติม: `remove all writing, calligraphy and red stamps, make it look more like an old painted legend`

### bg7 — ตะเกียบคีบสาหร่ายลื่น ๆ (ฉาก 7)

```
Vertical 9:16 photorealistic macro food photo of metal chopsticks lifting a long, glossy, slippery strand of dark green seaweed out of a bowl of Korean seaweed soup, the seaweed sliding off the chopsticks with broth droplets dripping down in mid-air, frozen motion. Main subject placed in the middle-upper part of the frame. The top 15% of the image is soft out-of-focus dark background, and the bottom 45% is an empty, blurred, softly lit dark area with the bowl rim fading out of focus. Warm cinematic lighting, deep navy blue shadows with warm butter-yellow highlights glinting on the wet seaweed, shallow depth of field, rich contrast, playful, eye-catching, high detail. No people, no faces, no text, no letters, no logo, no watermark.
```
คำอธิบาย: ตะเกียบคีบสาหร่ายแล้วมันลื่นไถลหลุด มีหยดน้ำซุปกลางอากาศ สื่อมุก "ลื่น = สอบไถลตก" (ถ้าเห็นมือคีบได้ ไม่เป็นไร แต่ต้องไม่เห็นหน้า)
ถ้าภาพออกมาไม่ดี ลองเติม: `make the seaweed look more slippery and sliding off, with drops falling`

---

## เช็กก่อนส่งภาพกลับ (ดูเร็ว ๆ)

- [ ] ภาพแนวตั้ง (สูงกว่ากว้าง)
- [ ] ไม่มีหน้าคน ไม่มีตัวหนังสือ/ลายน้ำ (ถ้ามีนิดหน่อยตรงขอบ ทีมตัด/เบลอให้ได้)
- [ ] ครึ่งล่างของภาพค่อนข้างโล่ง (ไว้ให้น้องนางาจิยืน)
