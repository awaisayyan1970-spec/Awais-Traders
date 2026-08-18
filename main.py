from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import hashlib

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Mock database for users, complaints, tickets, and staff
users_db = {
    "admin@awaistraders.com": hashlib.sha256("admin123".encode()).hexdigest()
}

staff_db = ["Isfaq", "Waqas", "Ayyan", "Jabari"]

complaints_db = []
tickets_db = []
active_sessions = set()

# Central Hub / Landing Page at Root URL
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return HTMLResponse("""
        <html>
            <head>
                <title>Awais Traders - ISP Portal</title>
                <style>
                    body { background: #0b0b0b; color: #d4af37; font-family: Arial; text-align: center; padding-top: 50px; }
                    .btn { display: inline-block; margin: 15px; padding: 15px 30px; background: #d4af37; color: #000; font-weight: bold; text-decoration: none; border-radius: 5px; font-size: 18px; }
                    .btn:hover { background: #fff; }
                </style>
            </head>
            <body>
                <h1>AWAIS TRADERS ISP OPERATIONS</h1>
                <p>Select your required portal below:</p>
                <br>
                <a href="/portal" class="btn">Customer Complaint Portal</a>
                <a href="/admin" class="btn">Admin & Staff Dashboard</a>
            </body>
        </html>
    """)

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html", {})

@app.post("/login")
def login_post(request: Request, email: str = Form(...), password: str = Form(...)):
    hashed_pwd = hashlib.sha256(password.encode()).hexdigest()
    if email in users_db and users_db[email] == hashed_pwd:
        active_sessions.add(email)
        response = RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(key="admin_session", value=email)
        return response
    return templates.TemplateResponse(request, "login.html", {"error": "Invalid Credentials"})

@app.get("/portal", response_class=HTMLResponse)
def complaint_form(request: Request):
    return templates.TemplateResponse(request, "complaint_form.html", {})

@app.post("/submit-complaint")
def submit_complaint(request: Request, phone: str = Form(...), address: str = Form(...), subscriber_id: str = Form(...), complaint_text: str = Form(...)):
    complaint_id = len(complaints_db) + 1
    complaints_db.append({
        "id": complaint_id,
        "phone": phone,
        "address": address,
        "subscriber_id": subscriber_id,
        "complaint": complaint_text,
        "status": "Pending"
    })
    return templates.TemplateResponse(request, "success.html", {})

@app.get("/admin", response_class=HTMLResponse)
def admin_panel(request: Request):
    session_email = request.cookies.get("admin_session")
    if not session_email or session_email not in active_sessions:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    return templates.TemplateResponse(request, "admin.html", {
        "complaints": complaints_db,
        "tickets": tickets_db,
        "staff_list": staff_db
    })

@app.post("/admin/create-ticket/{complaint_id}")
def create_ticket(request: Request, complaint_id: int, staff_name: str = Form(...)):
    session_email = request.cookies.get("admin_session")
    if not session_email or session_email not in active_sessions:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
        
    target_complaint = next((c for c in complaints_db if c["id"] == complaint_id), None)
    if target_complaint:
        target_complaint["status"] = "In Progress"
        ticket_id = len(tickets_db) + 1
        tickets_db.append({
            "ticket_id": ticket_id,
            "subscriber_id": target_complaint["subscriber_id"],
            "phone": target_complaint["phone"],
            "address": target_complaint["address"],
            "issue": target_complaint["complaint"],
            "assigned_staff": staff_name,
            "status": "Assigned"
        })
    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
