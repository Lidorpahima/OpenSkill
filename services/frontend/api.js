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
        await checkTokenExpiration(response);

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
    localStorage.removeItem("token");
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
