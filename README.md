# PathSense 🚀  
AI-powered Route Optimization & Place Management  

PathSense is a full-stack project that helps users manage places, optimize travel routes, and interact with an AI assistant.  
Built with **FastAPI (backend)** and **Next.js + Tailwind (frontend)**.  

---

## 📂 Project Structure



## 📖 Overview
**PathSense** helps users plan optimized travel routes by managing places, setting start & end points, and interacting with an AI-powered assistant.  
It combines a **modern single-page frontend** with a **robust FastAPI backend**, delivering smooth performance and a professional UI.

---

## ✨ Features
- ✅ Add, manage, and remove places  
- ✅ Set start & end points for trips  
- ✅ Optimize routes with return-to-start option  
- ✅ Interactive map visualization  
- ✅ AI-powered chat assistant  
- ✅ Responsive single-page UI with animations  

---

## 🛠 Tech Stack
**Frontend**
- Next.js 14  
- React  
- Tailwind CSS  
- shadcn/ui  

**Backend**
- FastAPI (Python 3.10+)  
- Uvicorn  

**Other**
- REST APIs for geocoding & optimization  

---

## 📂 Project Structure
```

PathSense/
│
├── backend/         # FastAPI app
│   ├── app/         # Routers, services, config
│   ├── main.py      # FastAPI entry point
│   └── requirements.txt
│
├── frontend/        # Next.js app
│   ├── src/         # Components & pages
│   ├── package.json
│   ├── next.config.ts
│   └── tsconfig.json
│
└── README.md

````

---

## ⚡ Setup Instructions

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/Shantanu-00/PathSense.git
cd PathSense
````

### 2️⃣ Backend (FastAPI)

```bash
cd backend
python -m venv venv
# Activate venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

👉 Runs at: **[http://localhost:8000]**

### 3️⃣ Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev
```

👉 Runs at: **[http://localhost:3000]**

---

## 🔗 API Endpoints

| Endpoint                  | Method | Description            |
| ------------------------- | ------ | ---------------------- |
| `/api/v1/places`          | GET    | List all places        |
| `/api/v1/places`          | POST   | Add a new place        |
| `/api/v1/set-start-end`   | POST   | Set start/end places   |
| `/api/v1/reset-start-end` | POST   | Reset start/end places |
| `/api/v1/optimize`        | POST   | Optimize route         |
| `/api/v1/chat`            | POST   | Chat with AI assistant |
| `/api/v1/geocode`         | POST   | Get coordinates        |

---

## 🚀 Deployment

* **Frontend** → [Vercel](https://vercel.com) 
* **Backend** → [Render](https://render.com) 

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!
Check the [issues](../../issues) page.

---

## 📜 License

This project is licensed under the **MIT License**.

---

## 👨‍💻 Author

Built  by Shantanu (https://github.com/Shantanu-00)
