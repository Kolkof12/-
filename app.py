<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SENTINEL-X | @WXL_E</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Cairo:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
        :root { --neon: #ff003c; --bg: #050505; --grid: #111; }
        body { background: var(--bg); color: #fff; font-family: 'Cairo', sans-serif; margin: 0; overflow-x: hidden; }
        body::before { content: ""; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(rgba(255,0,60,0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(255,0,60,0.05) 1px, transparent 1px); background-size: 30px 30px; z-index: -1; }

        .container { max-width: 1200px; margin: auto; padding: 20px; }
        
        /* نظام الدخول */
        #authScreen { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: var(--bg); z-index: 5000; display: flex; align-items: center; justify-content: center; }
        .auth-box { background: #0a0a0a; padding: 40px; border: 1px solid var(--neon); border-radius: 20px; text-align: center; width: 320px; box-shadow: 0 0 20px var(--neon); }

        /* البطاقة الاحترافية */
        .card {
            background: linear-gradient(135deg, #0f0f0f 0%, #1a0005 100%);
            border: 1px solid var(--neon); border-radius: 25px; padding: 30px;
            width: 350px; margin: 20px auto; position: relative; overflow: hidden;
            box-shadow: 0 10px 40px rgba(255,0,60,0.2);
        }
        .card::after { content: "NINJA"; position: absolute; right: -20px; bottom: -10px; font-family: 'Orbitron'; font-size: 5rem; color: rgba(255,0,60,0.05); transform: rotate(-10deg); }
        .rank { background: var(--neon); color: #fff; padding: 2px 15px; border-radius: 50px; font-family: 'Orbitron'; font-size: 0.7rem; font-weight: 900; }
        .points { font-size: 3.5rem; font-weight: 900; font-family: 'Orbitron'; text-align: center; margin: 10px 0; color: #fff; text-shadow: 0 0 10px var(--neon); }

        /* المتجر */
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 25px; margin-top: 40px; }
        .p-card { background: #0d0d0d; border-radius: 15px; border: 1px solid #222; overflow: hidden; transition: 0.4s; }
        .p-card:hover { border-color: var(--neon); transform: translateY(-10px); }
        .p-img { width: 100%; height: 180px; object-fit: cover; filter: grayscale(50%); transition: 0.4s; }
        .p-card:hover .p-img { filter: grayscale(0%); }
        .p-info { padding: 20px; text-align: center; }

        .btn { background: var(--neon); color: #fff; padding: 12px; border: none; border-radius: 8px; font-weight: 900; cursor: pointer; width: 100%; font-family: 'Cairo'; transition: 0.3s; }
        .btn:hover { letter-spacing: 2px; box-shadow: 0 0 15px var(--neon); }

        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.95); z-index: 3000; }
        .modal-content { background: #0a0a0a; width: 90%; max-width: 400px; margin: 50px auto; padding: 30px; border: 1px solid var(--neon); border-radius: 20px; text-align: center; }
        input { width: 100%; padding: 12px; margin: 10px 0; background: #000; border: 1px solid #333; color: #fff; border-radius: 8px; box-sizing: border-box; }
    </style>
</head>
<body>

<div id="authScreen">
    <div class="auth-box">
        <h1 style="font-family: 'Orbitron'; color: var(--neon);">SENTINEL LOGIN</h1>
        <input type="email" id="logEmail" placeholder="الإيميل">
        <input type="password" id="logPass" placeholder="كلمة المرور">
        <button class="btn" onclick="login()">دخول / إنشاء حساب</button>
        <p style="font-size: 0.7rem; color: #555; margin-top: 10px;">@WXL_E RIGHTS RESERVED</p>
    </div>
</div>

<div class="container">
    <header style="text-align: center; margin-bottom: 30px;">
        <h1 style="font-family: 'Orbitron'; font-size: 2.5rem; margin: 0;">SENTINEL<span style="color: var(--neon);">-X</span></h1>
        <p style="color: #666; letter-spacing: 5px;">SHADOW NETWORK BY @WXL_E</p>
    </header>

    <div class="card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span class="rank" id="rankName">AGENT</span>
            <span style="font-family: 'Orbitron'; font-size: 0.8rem;" id="dispEmail">USER@WXL</span>
        </div>
        <div class="points" id="dispPoints">000</div>
        <div style="text-align: center; color: var(--neon); font-family: 'Orbitron'; font-size: 0.7rem;">CREDITS AVAILABLE</div>
        <div style="margin-top: 20px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 10px; display: flex; justify-content: space-between;">
            <small style="color: #444;">SECURITY PIN:</small>
            <small id="dispPIN" style="color: var(--neon); font-weight: bold;"></small>
        </div>
    </div>

    <div style="display: flex; gap: 15px; justify-content: center;">
        <button class="btn" style="width: auto; padding: 10px 30px;" onclick="claimDaily()">🎁 منحة يومية</button>
        <button class="btn" style="width: auto; padding: 10px 30px; background: transparent; border: 1px solid var(--neon);" onclick="copyRef()">🔗 دعوة أصدقاء</button>
    </div>

    <div class="grid" id="shopGrid"></div>
</div>

<div id="buyModal" class="modal">
    <div class="modal-content">
        <h2 style="font-family: 'Orbitron'; color: var(--neon);">PURCHASE GATE</h2>
        <input type="text" id="botToken" placeholder="Bot Token">
        <input type="text" id="chatID" placeholder="Chat ID">
        <input type="password" id="checkPIN" placeholder="أدخل PIN البطاقة">
        <button class="btn" id="confirmBtn">شراء وإرسال الملف</button>
        <button onclick="closeModal()" style="background:none; color:#444; border:none; cursor:pointer; margin-top:10px;">إلغاء</button>
    </div>
</div>

<script>
    let user = null;

    function login() {
        const email = document.getElementById('logEmail').value;
        const pass = document.getElementById('logPass').value;
        if(!email || !pass) return alert("املاً البيانات!");

        // جلب البيانات من LocalStorage بناءً على الإيميل (حساب حقيقي)
        let saved = JSON.parse(localStorage.getItem('user_' + email));
        if(saved) {
            if(saved.pass !== pass) return alert("كلمة المرور خاطئة!");
            user = saved;
        } else {
            user = {
                email: email.toUpperCase(),
                pass: pass,
                points: 500,
                pin: Math.floor(1000 + Math.random() * 9000),
                daily: 0
            };
            saveUser();
        }
        document.getElementById('authScreen').style.display = 'none';
        updateUI();
    }

    function saveUser() {
        localStorage.setItem('user_' + user.email.toLowerCase(), JSON.stringify(user));
        updateUI();
    }

    function updateUI() {
        document.getElementById('dispEmail').innerText = user.email;
        document.getElementById('dispPoints').innerText = user.points;
        document.getElementById('dispPIN').innerText = user.pin;
        let r = "AGENT";
        if(user.points > 2000) r = "ELITE NINJA"; else if(user.points > 1000) r = "SHADOW";
        document.getElementById('rankName').innerText = r;
    }

    const products = [
        {id:1, name:"IPGRAM.py", price:150, img:"https://images.unsplash.com/photo-1558494949-ef010cbdcc51?w=400", fileUrl:"https://raw.githubusercontent.com/username/repo/main/IPGRAM.py"},
        {id:2, name:"solx_wxle.py", price:350, img:"https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=400", fileUrl:"https://raw.githubusercontent.com/username/repo/main/solx_wxle.py"},
        {id:3, name:"RSS.DDOS.V3.py", price:200, img:"https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=400", fileUrl:"https://raw.githubusercontent.com/username/repo/main/RSS.DDOS.V3.py"},
        {id:4, name:"كورس الاختراق الشامل", price:800, img:"https://images.unsplash.com/photo-1563986768609-322da13575f3?w=400", fileUrl:"HACK_COURSE_LINK", isLink:true},
        {id:5, name:"كورس التداول الاحترافي", price:900, img:"https://images.unsplash.com/photo-1611974717483-9b910c0c9cd9?w=400", fileUrl:"TRADE_COURSE_LINK", isLink:true}
    ];

    let activeP = null;
    function openBuy(id) {
        activeP = products.find(p => p.id === id);
        if(user.points < activeP.price) return alert("نقاطك لا تكفي!");
        document.getElementById('buyModal').style.display = "block";
    }

    function closeModal() { document.getElementById('buyModal').style.display = "none"; }

    document.getElementById('confirmBtn').onclick = async function() {
        const pin = document.getElementById('checkPIN').value;
        const token = document.getElementById('botToken').value;
        const cid = document.getElementById('chatID').value;
        
        if(pin != user.pin) return alert("PIN خاطئ!");

        user.points -= activeP.price;
        saveUser();

        // إرسال الملف الفعلي أو الرابط
        const method = activeP.isLink ? 'sendMessage' : 'sendDocument';
        const key = activeP.isLink ? 'text' : 'document';
        const url = `https://api.telegram.org/bot${token}/${method}`;
        
        try {
            await fetch(url, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    chat_id: cid,
                    [key]: activeP.fileUrl,
                    caption: `✅ تم الشراء: ${activeP.name}\nالمشتري: ${user.email}\nالمطور: @WXL_E`
                })
            });
            alert("تم! الملف وصلك الآن في البوت.");
            closeModal();
        } catch(e) { alert("خطأ في البوت!"); }
    }

    function claimDaily() {
        if(Date.now() - user.daily < 86400000) return alert("عد لاحقاً!");
        user.points += 200; user.daily = Date.now(); saveUser();
        alert("تمت إضافة 200 نقطة!");
    }

    const grid = document.getElementById('shopGrid');
    products.forEach(p => {
        grid.innerHTML += `
            <div class="p-card">
                <img src="${p.img}" class="p-img">
                <div class="p-info">
                    <h3 style="font-family:'Orbitron'">${p.name}</h3>
                    <div style="color:var(--neon); margin-bottom:15px">${p.price} CREDITS</div>
                    <button class="btn" onclick="openBuy(${p.id})">PURCHASE</button>
                </div>
            </div>`;
    });
</script>
</body>
</html>
