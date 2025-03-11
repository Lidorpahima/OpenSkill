const API_BASE_URL = "http://localhost:8080";

async function login(email, password) {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });
        
        if (!response.ok) {
            await checkTokenExpiration(response);
            const errorData = await response.json();
            throw new Error(errorData.detail || "שגיאה בהתחברות");
        }
        
        const data = await response.json();
        localStorage.setItem("token", data.access_token);
        localStorage.setItem("tokenExpiry", new Date(Date.now() + 30 * 60 * 1000).toString());
        const userInfo = await getUserInfo(data.access_token);
        return { 
            success: true, 
            user: userInfo,
            token: data.access_token
        };
    } catch (error) {
        console.error("שגיאת התחברות:", error);
        return { success: false, message: error.message };
    }
}

async function register(username, email, password) {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, email, password })
        });
        
        if (!response.ok) {
            await checkTokenExpiration(response);
            const errorData = await response.json();
            throw new Error(errorData.detail || "שגיאה ברישום משתמש");
        }
        
        return { success: true, data: await response.json() };
    } catch (error) {
        console.error("שגיאת רישום:", error);
        return { success: false, message: error.message };
    }
}

async function getUserInfo(token) {
    try {
        return {
            username: "משתמש",
            email: "user@example.com"
        };
    } catch (error) {
        console.error("שגיאה בקבלת מידע על המשתמש:", error);
        throw error;
    }
}

async function apiRequest(url, options = {}) {
    try {
        const token = localStorage.getItem("token");
        if (!token) throw new Error("נדרשת התחברות");
        
        options.headers = {
            ...options.headers,
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        };

        console.log("🚀 Sending API request:");
        console.log("🔗 URL:", `${API_BASE_URL}${url}`);
        console.log("📑 Headers:", options.headers);

        const response = await fetch(`${API_BASE_URL}${url}`, options);
        const tokenValid = await checkTokenExpiration(response);
        
        // אם הטוקן התחדש, ננסה שוב את הבקשה
        if (response.status === 401 && tokenValid) {
            // הטוקן חודש, ננסה שוב את הבקשה
            const newToken = localStorage.getItem("token");
            options.headers["Authorization"] = `Bearer ${newToken}`;
            const newResponse = await fetch(`${API_BASE_URL}${url}`, options);
            
            if (!newResponse.ok) {
                const errorData = await newResponse.json();
                throw new Error(errorData.detail || "שגיאה בבקשה לשרת");
            }
            
            return await newResponse.json();
        }

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || "שגיאה בבקשה לשרת");
        }

        return await response.json();
    } catch (error) {
        console.error("שגיאה בבקשה לשרת:", error);
        throw error;
    }
}


async function getLearningGoals() {
    return await apiRequest("/learning/goals/");
}

async function createLearningGoal(title, description) {
    return await apiRequest("/learning/create_goal/", {
        method: "POST",
        body: JSON.stringify({ title, description })
    });
}

async function sendChatMessage(message) {
    console.log("Sending message:", message); 
    console.log("Token:", localStorage.getItem("token"));  
    
    return await apiRequest("/ai_chat/chat/", {
        method: "POST",
        body: JSON.stringify({ message }) 
    });
}

async function getCareerRecommendations() {
    return await apiRequest("/ai_chat/career_recommendations/");
}

async function selectCareer(careerId) {
    return await apiRequest("/ai_chat/select_career/", {
        method: "POST",
        body: JSON.stringify({ career_id: careerId })
    });
}

function logout() {
    const user = JSON.parse(sessionStorage.getItem("user"));
    const userId = user ? user.id || 'anonymous' : 'anonymous';

    localStorage.removeItem(`chatHistory_${userId}`);

    localStorage.removeItem("token");
    sessionStorage.removeItem("user");
    
    return { success: true };
}
async function checkTokenExpiration(response) {
    if (response.status === 401) {
        showPopup("ההתחברות שלך פגה תוקף. יש להתחבר מחדש.");
        localStorage.removeItem("token");
        sessionStorage.removeItem("user");
        
        setTimeout(() => {
            navigate("login");
        }, 2000);
    }
}
async function checkTokenExpiration(response) {
    if (response?.status === 401) {
        const shouldRefresh = await showConfirmPopup("פג תוקף ההתחברות שלך. האם ברצונך להישאר מחובר?");
        
        if (shouldRefresh) {
            const refreshResult = await refreshToken();
            if (refreshResult.success) {
                showPopup("התחברות חודשה בהצלחה!");
                return true; // הטוקן חודש בהצלחה
            } else {
                showPopup(refreshResult.message || "לא הצלחנו לחדש את ההתחברות");
            }
        }
        
        // לא ניתן לרענן, או שהמשתמש סירב, או שהריענון נכשל
        localStorage.removeItem("token");
        sessionStorage.removeItem("user");
        
        setTimeout(() => {
            navigate("login");
        }, 2000);
        
        return false;
    }
    return true; // אין בעיה עם הטוקן
}
function showConfirmPopup(message) {
    return new Promise((resolve) => {
        const popup = document.createElement("div");
        popup.classList.add("popup");
        popup.innerHTML = `
            <div class="popup-content">
                <p>${message}</p>
                <div class="popup-buttons">
                    <button id="popupConfirm">כן</button>
                    <button id="popupCancel">לא</button>
                </div>
            </div>
        `;
        document.body.appendChild(popup);

        document.getElementById("popupConfirm").addEventListener("click", () => {
            popup.remove();
            resolve(true);
        });

        document.getElementById("popupCancel").addEventListener("click", () => {
            popup.remove();
            resolve(false);
        });
    });
}