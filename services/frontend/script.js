// יצירת דפי האפליקציה
const routes = {
    "login": `
        <div class="container">
            <h1>ברוך הבא ל-UPSKILL</h1>
            <form id="loginForm">
                <input type="email" id="email" placeholder="אימייל" required>
                <input type="password" id="password" placeholder="סיסמה" required>
                <button type="submit">התחבר</button>
            </form>
            <p>עדיין אין לך חשבון? <a href="#" id="goToRegister">הירשם עכשיו</a></p>
            <p id="errorMessage" class="error-message"></p>
        </div>
    `,
    "register": `
        <div class="container">
            <h1>הרשמה למערכת</h1>
            <form id="registerForm">
                <input type="text" id="username" placeholder="שם משתמש" required>
                <input type="email" id="email" placeholder="אימייל" required>
                <input type="password" id="password" placeholder="סיסמה" required>
                <button type="submit">הירשם</button>
            </form>
            <p>כבר יש לך חשבון? <a href="#" id="goToLogin">התחבר כאן</a></p>
            <p id="errorMessage" class="error-message"></p>
        </div>
    `,
    "dashboard": `
        <div class="container dashboard">
            <h1>ברוך הבא, <span id="username"></span>!</h1>
            <div class="dashboard-menu">
                <button id="btnGoals">מטרות למידה</button>
                <button id="btnChat">צ'אט AI</button>
                <button id="btnCareer">מסלול קריירה</button>
                <button id="logout" class="logout-btn">התנתק</button>
            </div>
            <div id="dashboardContent"></div>
        </div>
    `,
    "goals": `
        <div class="goals-container">
            <h2>מטרות הלמידה שלי</h2>
            <div id="goalsList"></div>
            <button id="addGoalBtn">הוסף מטרה חדשה</button>
            <div id="addGoalForm" class="hidden">
                <input type="text" id="goalTitle" placeholder="כותרת המטרה">
                <textarea id="goalDescription" placeholder="תיאור המטרה"></textarea>
                <button id="saveGoalBtn">שמור</button>
                <button id="cancelGoalBtn">בטל</button>
            </div>
        </div>
    `,
    "chat": `
        <div class="chat-container">
            <h2>צ'אט עם AI</h2>
            <div id="chatHistory" class="chat-history"></div>
            <div class="chat-input">
                <input type="text" id="chatMessage" placeholder="הקלד את השאלה שלך...">
                <button id="sendChatBtn">שלח</button>
            </div>
            <div id="careerRecommendations" class="hidden">
                <h3>המלצות קריירה</h3>
                <div id="recommendationsList"></div>
            </div>
        </div>
    `,
    "career": `
        <div class="career-container">
            <h2>המסלול המקצועי שלי</h2>
            <div id="careerPath"></div>
        </div>
    `
};

// פונקציה לניווט בין דפים
function navigate(page) {
    const app = document.getElementById("app");
    app.classList.add("hidden"); // אנימציה למעבר דף
    setTimeout(() => {
        app.innerHTML = routes[page]; // טוען את הדף החדש
        app.classList.remove("hidden"); 

        if (page === "login") setupLogin();
        if (page === "register") setupRegister();
        if (page === "dashboard") setupDashboard();
        if (page === "goals") setupGoals();
        if (page === "chat") setupChat();
        if (page === "career") setupCareer();
    }, 300);
}

// פונקציה לניהול התחברות
function setupLogin() {
    document.getElementById("loginForm").addEventListener("submit", async function(event) {
        event.preventDefault();
        
        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;
        const errorMessage = document.getElementById("errorMessage");
        
        errorMessage.textContent = "";
        
        try {
            const result = await login(email, password);
            if (result.success) {
                // שמור מידע משתמש ב-sessionStorage
                sessionStorage.setItem("user", JSON.stringify(result.user));
                sessionStorage.setItem("token", result.token);
                navigate("dashboard");
            } else {
                errorMessage.textContent = result.message || "שם משתמש או סיסמה שגויים";
            }
        } catch (error) {
            errorMessage.textContent = "שגיאה בהתחברות: " + error.message;
        }
    });
    
    document.getElementById("goToRegister").addEventListener("click", function(event) {
        event.preventDefault();
        navigate("register");
    });
}

// פונקציה לניהול הרשמה
function setupRegister() {
    document.getElementById("registerForm").addEventListener("submit", async function(event) {
        event.preventDefault();
        
        const username = document.getElementById("username").value;
        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;
        const errorMessage = document.getElementById("errorMessage");
        
        errorMessage.textContent = "";
        
        try {
            const result = await register(username, email, password);
            if (result.success) {
                navigate("login");
                alert("הרשמה בוצעה בהצלחה! אנא התחבר עם האימייל והסיסמה שלך.");
            } else {
                errorMessage.textContent = result.message || "שגיאה ברישום המשתמש";
            }
        } catch (error) {
            errorMessage.textContent = "שגיאה ברישום: " + error.message;
        }
    });
    
    document.getElementById("goToLogin").addEventListener("click", function(event) {
        event.preventDefault();
        navigate("login");
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
    
    // תפריט ניווט בדשבורד
    document.getElementById("btnGoals").addEventListener("click", () => {
        document.getElementById("dashboardContent").innerHTML = routes["goals"];
        setupGoals();
    });
    
    document.getElementById("btnChat").addEventListener("click", () => {
        document.getElementById("dashboardContent").innerHTML = routes["chat"];
        setupChat();
    });
    
    document.getElementById("btnCareer").addEventListener("click", () => {
        document.getElementById("dashboardContent").innerHTML = routes["career"];
        setupCareer();
    });
    
    document.getElementById("logout").addEventListener("click", () => {
        logout();
        sessionStorage.removeItem("user");
        sessionStorage.removeItem("token");
        navigate("login");
    });
    
    // טען את דף המטרות כברירת מחדל
    document.getElementById("dashboardContent").innerHTML = routes["goals"];
    setupGoals();
}

// פונקציה לניהול מטרות למידה
async function setupGoals() {
    try {
        const goals = await getLearningGoals();
        const goalsList = document.getElementById("goalsList");
        
        if (goals.length === 0) {
            goalsList.innerHTML = "<p>אין לך עדיין מטרות למידה. הוסף את המטרה הראשונה שלך!</p>";
        } else {
            goalsList.innerHTML = goals.map(goal => `
                <div class="goal-item">
                    <h3>${goal.title}</h3>
                    <p>${goal.description}</p>
                    <div class="goal-progress">
                        <div class="progress-bar" style="width: ${goal.progress}%"></div>
                    </div>
                    <p>התקדמות: ${goal.progress}%</p>
                </div>
            `).join("");
        }
        
        document.getElementById("addGoalBtn").addEventListener("click", () => {
            document.getElementById("addGoalForm").classList.remove("hidden");
        });
        
        document.getElementById("saveGoalBtn").addEventListener("click", async () => {
            const title = document.getElementById("goalTitle").value;
            const description = document.getElementById("goalDescription").value;
            
            if (!title || !description) {
                alert("נא למלא את כל השדות");
                return;
            }
            
            try {
                await createLearningGoal(title, description);
                document.getElementById("addGoalForm").classList.add("hidden");
                setupGoals(); // רענן את רשימת המטרות
            } catch (error) {
                alert("שגיאה ביצירת מטרה: " + error.message);
            }
        });
        
        document.getElementById("cancelGoalBtn").addEventListener("click", () => {
            document.getElementById("addGoalForm").classList.add("hidden");
        });
        
    } catch (error) {
        console.error("שגיאה בטעינת מטרות:", error);
        document.getElementById("goalsList").innerHTML = "<p>שגיאה בטעינת מטרות הלמידה</p>";
    }
}

// פונקציה לניהול צ'אט AI
function setupChat() {
    const chatHistory = document.getElementById("chatHistory");
    const chatInput = document.getElementById("chatMessage");
    const sendButton = document.getElementById("sendChatBtn");
    
    // טען היסטוריית צ'אט מאחסון מקומי אם קיימת
    const storedHistory = localStorage.getItem("chatHistory");
    if (storedHistory) {
        chatHistory.innerHTML = storedHistory;
    }
    
    sendButton.addEventListener("click", async () => {
        const message = chatInput.value.trim();
        if (!message) return;
        
        // הוסף הודעת המשתמש לצ'אט
        chatHistory.innerHTML += `<div class="user-message">משתמש: ${message}</div>`;
        chatInput.value = "";
        
        try {
            const response = await sendChatMessage(message);
            
            // הוסף תגובת AI לצ'אט
            chatHistory.innerHTML += `<div class="ai-message">AI: ${response.response}</div>`;
            
            // שמור היסטוריית צ'אט באחסון מקומי
            localStorage.setItem("chatHistory", chatHistory.innerHTML);
            
            // בדוק אם יש המלצות קריירה
            if (response.recommendation && response.recommendation.length > 0) {
                const recommendationsDiv = document.getElementById("careerRecommendations");
                const recommendationsList = document.getElementById("recommendationsList");
                
                recommendationsDiv.classList.remove("hidden");
                recommendationsList.innerHTML = response.recommendation.map((career, index) => `
                    <div class="career-recommendation">
                        <h4>${career.title} (${career.match_percentage}% התאמה)</h4>
                        <p>${career.description}</p>
                        <button class="select-career-btn" data-id="${index + 1}">בחר קריירה זו</button>
                    </div>
                `).join("");
                
                // הוסף אירועי לחיצה על כפתורי בחירת קריירה
                document.querySelectorAll(".select-career-btn").forEach(button => {
                    button.addEventListener("click", async () => {
                        const careerId = button.getAttribute("data-id");
                        try {
                            const result = await selectCareer(parseInt(careerId));
                            alert(result.message || "הקריירה נבחרה בהצלחה!");
                            navigate("career");
                        } catch (error) {
                            alert("שגיאה בבחירת קריירה: " + error.message);
                        }
                    });
                });
            }
            
        } catch (error) {
            chatHistory.innerHTML += `<div class="error-message">שגיאה: ${error.message}</div>`;
        }
        
        // גלול לתחתית הצ'אט
        chatHistory.scrollTop = chatHistory.scrollHeight;
    });
    
    // אפשר לשלוח הודעה באמצעות Enter
    chatInput.addEventListener("keypress", (event) => {
        if (event.key === "Enter") {
            sendButton.click();
        }
    });
}

// פונקציה לניהול דף קריירה
async function setupCareer() {
    const careerPathDiv = document.getElementById("careerPath");
    
    try {
        // נסה לקבל המלצות קריירה
        const recommendations = await getCareerRecommendations();
        
        if (recommendations && recommendations.length > 0) {
            const selectedCareer = recommendations[0]; // לשם הדוגמה, נשתמש בקריירה הראשונה
            
            careerPathDiv.innerHTML = `
                <div class="selected-career">
                    <h3>המסלול שבחרת: ${selectedCareer.title}</h3>
                    <p>${selectedCareer.description}</p>
                    <div class="match-percentage">התאמה: ${selectedCareer.match_percentage}%</div>
                </div>
                <div class="learning-path">
                    <h3>מסלול הלמידה המומלץ:</h3>
                    <ol>
                        <li>למד יסודות ${selectedCareer.title}</li>
                        <li>השלם קורסים בסיסיים</li>
                        <li>צבור ניסיון בפרויקטים</li>
                        <li>פתח תיק עבודות</li>
                        <li>התכונן לראיונות עבודה</li>
                    </ol>
                </div>
            `;
        } else {
            careerPathDiv.innerHTML = `
                <p>עדיין לא בחרת מסלול קריירה.</p>
                <p>גש לצ'אט ה-AI כדי לקבל המלצות קריירה!</p>
                <button id="goToChatBtn" class="action-btn">למעבר לצ'אט</button>
            `;
            
            document.getElementById("goToChatBtn").addEventListener("click", () => {
                document.getElementById("btnChat").click();
            });
        }
    } catch (error) {
        console.error("שגיאה בטעינת נתיב קריירה:", error);
        careerPathDiv.innerHTML = "<p>שגיאה בטעינת נתיב הקריירה שלך</p>";
    }
}

// הפעלת המערכת - טעינת מסך מתאים
navigate(sessionStorage.getItem("token") ? "dashboard" : "login");

function showPopup(message) {
    const popup = document.createElement("div");
    popup.classList.add("popup");
    popup.innerHTML = `
        <div class="popup-content">
            <p>${message}</p>
            <button id="popupClose">אישור</button>
        </div>
    `;
    document.body.appendChild(popup);

    document.getElementById("popupClose").addEventListener("click", () => {
        popup.remove();
    });
}
