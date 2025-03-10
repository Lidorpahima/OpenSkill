// יצירת דפי האפליקציה
const routes = {
    "login": `
        <div class="container">
            <h1>Welcome Back</h1>
            <form id="loginForm">
                <input type="text" id="username" placeholder="Email" required>
                <input type="password" id="password" placeholder="Password" required>
                <button type="submit">Login</button>
            </form>
            <p id="errorMessage" style="color: red;"></p>
        </div>
    `,
    "dashboard": `
        <div class="container">
            <h1>ברוך הבא, <span id="username"></span>!</h1>
            <p>זהו הדשבורד שלך.</p>
            <button id="logout">התנתק</button>
        </div>
    `
};

function navigate(page) {
    const app = document.getElementById("app");
    app.classList.add("hidden"); // אנימציה למעבר דף
    setTimeout(() => {
        app.innerHTML = routes[page]; // טוען את הדף החדש
        app.classList.remove("hidden"); 

        if (page === "login") setupLogin();
        if (page === "dashboard") setupDashboard();
    }, 300);
}

// פונקציה לניהול התחברות
function setupLogin() {
    document.getElementById("loginForm").addEventListener("submit", async function(event) {
        event.preventDefault();
        const username = document.getElementById("username").value;
        const password = document.getElementById("password").value;

        const result = await login(username, password);
        if (result.success) {
            sessionStorage.setItem("user", JSON.stringify(result.user));
            navigate("dashboard");
        } else {
            document.getElementById("errorMessage").textContent = "שם משתמש או סיסמה שגויים";
        }
    });
}

// פונקציה לניהול הדשבורד
function setupDashboard() {
    const user = JSON.parse(sessionStorage.getItem("user"));
    if (!user) {
        navigate("login");
        return;
    }
    document.getElementById("username").textContent = user.username;
    document.getElementById("logout").addEventListener("click", () => {
        sessionStorage.removeItem("user");
        navigate("login");
    });
}

// הפעלת המערכת - טעינת מסך מתאים
navigate(sessionStorage.getItem("user") ? "dashboard" : "login");
