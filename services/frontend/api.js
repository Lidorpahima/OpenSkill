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
            throw new Error(errorData.detail || "Login failed");
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
        console.error("Login error:", error);
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
            throw new Error(errorData.detail || "Registration failed");
        }
        
        return { success: true, data: await response.json() };
    } catch (error) {
        console.error("Registration error:", error);
        return { success: false, message: error.message };
    }
}

async function getUserInfo(token) {
    try {
        return {
            username: "User",
            email: "user@example.com"
        };
    } catch (error) {
        console.error("Error fetching user info:", error);
        throw error;
    }
}

async function apiRequest(url, options = {}) {
    showLoadingSpinner();
    try {
        const token = localStorage.getItem("token");
        if (!token) throw new Error("Authentication required");
        
        options.headers = {
            ...options.headers,
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        };

        const response = await fetch(`${API_BASE_URL}${url}`, options);
        const tokenValid = await checkTokenExpiration(response);
        
        if (response.status === 401 && tokenValid) {
            const newToken = localStorage.getItem("token");
            options.headers["Authorization"] = `Bearer ${newToken}`;
            const newResponse = await fetch(`${API_BASE_URL}${url}`, options);
            
            if (!newResponse.ok) {
                const errorData = await newResponse.json();
                throw new Error(errorData.detail || "Server request failed");
            }
            
            return await newResponse.json();
        }

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || "Server request failed");
        }

        return await response.json();
    } catch (error) {
        console.error("API request error:", error);
        throw error;
    } finally {
        hideLoadingSpinner();
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
    const user = JSON.parse(sessionStorage.getItem("user"));
    const userId = user ? user.id || 'anonymous' : 'anonymous';

    localStorage.removeItem(`chatHistory_${userId}`);
    localStorage.removeItem("token");
    sessionStorage.removeItem("user");
    
    return { success: true };
}

async function checkTokenExpiration(response) {
    if (response?.status === 401) {
        const shouldRefresh = await showConfirmPopup("Your session has expired. Would you like to stay logged in?");
        
        if (shouldRefresh) {
            const refreshResult = await refreshToken();
            if (refreshResult.success) {
                showPopup("Session renewed successfully!");
                return true;
            } else {
                showPopup(refreshResult.message || "Failed to renew session");
            }
        }
        
        localStorage.removeItem("token");
        sessionStorage.removeItem("user");
        
        setTimeout(() => {
            navigate("login");
        }, 2000);
        
        return false;
    }
    return true;
}

async function refreshToken() {
    // Placeholder for token refresh logic
    return { success: false, message: "Token refresh not implemented" };
}

function showConfirmPopup(message) {
    return new Promise((resolve) => {
        const popup = document.createElement("div");
        popup.classList.add("popup");
        popup.innerHTML = `
            <div class="popup-content">
                <p>${message}</p>
                <div class="popup-buttons">
                    <button id="popupConfirm">Yes</button>
                    <button id="popupCancel">No</button>
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

function showLoadingSpinner() {
    const container = document.getElementById("notification-container");
    container.innerHTML = `
        <div class="spinner">
            <i class="fas fa-spinner fa-spin"></i>
        </div>
    `;
}

function hideLoadingSpinner() {
    const container = document.getElementById("notification-container");
    container.innerHTML = "";
}