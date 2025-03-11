const routes = {
    "login": `
        <div class="container">
            <h1>Welcome to UPSKILL</h1>
            <form id="loginForm">
                <input type="email" id="email" placeholder="Email" required>
                <input type="password" id="password" placeholder="Password" required>
                <button type="submit">Login</button>
            </form>
            <p>Don't have an account? <a href="#" id="goToRegister">Register now</a></p>
            <p id="errorMessage" class="error-message"></p>
        </div>
    `,
    "register": `
        <div class="container">
            <h1>Register to UPSKILL</h1>
            <form id="registerForm">
                <input type="text" id="username" placeholder="Username" required>
                <input type="email" id="email" placeholder="Email" required>
                <input type="password" id="password" placeholder="Password" required>
                <button type="submit">Register</button>
            </form>
            <p>Already have an account? <a href="#" id="goToLogin">Login here</a></p>
            <p id="errorMessage" class="error-message"></p>
        </div>
    `,
    "dashboard": `
        <div class="container dashboard">
            <h1>Welcome, <span id="username"></span>!</h1>
            <div class="dashboard-menu">
                <button id="btnGoals">Learning Goals</button>
                <button id="btnChat">AI Chat</button>
                <button id="btnCareer">Career Path</button>
            </div>
            <div id="dashboardContent"></div>
        </div>
    `,
    "goals": `
        <div class="goals-container">
            <h2>My Learning Goals</h2>
            <div id="goalsList"></div>
            <button id="addGoalBtn">Add New Goal</button>
            <div id="addGoalForm" class="hidden">
                <input type="text" id="goalTitle" placeholder="Goal Title">
                <textarea id="goalDescription" placeholder="Goal Description"></textarea>
                <button id="saveGoalBtn">Save</button>
                <button id="cancelGoalBtn">Cancel</button>
            </div>
        </div>
    `,
    "chat": `
        <div class="chat-container">
            <h2>AI Chat</h2>
            <div id="chatHistory" class="chat-history"></div>
            <div class="chat-input">
                <input type="text" id="chatMessage" placeholder="What career path are you considering? Share your thoughts...">
                <button id="sendChatBtn">Send</button>
            </div>
            <div id="careerRecommendations" class="hidden">
                <h3>Career Recommendations</h3>
                <div id="recommendationsList"></div>
            </div>
        </div>
    `,
    "career": `
        <div class="career-container">
            <h2>My Career Path</h2>
            <div id="careerPath"></div>
        </div>
    `
};

function navigate(page) {
    const app = document.getElementById("app");
    app.classList.add("fade-out");
    setTimeout(() => {
        app.innerHTML = routes[page];
        app.classList.remove("fade-out");
        app.classList.add("fade-in");
        
        if (page === "login") setupLogin();
        if (page === "register") setupRegister();
        if (page === "dashboard") setupDashboard();
        if (page === "goals") setupGoals();
        if (page === "chat") setupChat();
        if (page === "career") setupCareer();
        
        // Update logout button visibility
        const logoutBtn = document.getElementById("logoutBtn");
        logoutBtn.classList.toggle("hidden", page === "login" || page === "register");
    }, 300);
}

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
                sessionStorage.setItem("user", JSON.stringify(result.user));
                sessionStorage.setItem("token", result.token);
                navigate("dashboard");
            } else {
                errorMessage.textContent = result.message || "Invalid credentials";
            }
        } catch (error) {
            errorMessage.textContent = "Login error: " + error.message;
        }
    });
    
    document.getElementById("goToRegister").addEventListener("click", function(event) {
        event.preventDefault();
        navigate("register");
    });
}

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
                showPopup("Registration successful! Please login.");
            } else {
                errorMessage.textContent = result.message || "Registration failed";
            }
        } catch (error) {
            errorMessage.textContent = "Registration error: " + error.message;
        }
    });
    
    document.getElementById("goToLogin").addEventListener("click", function(event) {
        event.preventDefault();
        navigate("login");
    });
}

function setupDashboard() {
    const user = JSON.parse(sessionStorage.getItem("user"));
    if (!user) {
        navigate("login");
        return;
    }
    
    document.getElementById("username").textContent = user.username;
    
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
    
    document.getElementById("logoutBtn").addEventListener("click", () => {
        logout();
        sessionStorage.removeItem("user");
        sessionStorage.removeItem("token");
        navigate("login");
    });
    
    document.getElementById("dashboardContent").innerHTML = routes["goals"];
    setupGoals();
}

async function setupGoals() {
    try {
        const goals = await getLearningGoals();
        const goalsList = document.getElementById("goalsList");
        
        if (goals.length === 0) {
            goalsList.innerHTML = "<p>You don't have any learning goals yet. Add your first goal!</p>";
        } else {
            goalsList.innerHTML = goals.map(goal => `
                <div class="goal-item fade-in">
                    <h3>${goal.title}</h3>
                    <p>${goal.description}</p>
                    <div class="goal-progress">
                        <div class="progress-bar" style="width: ${goal.progress}%"></div>
                    </div>
                    <p>Progress: ${goal.progress}%</p>
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
                showPopup("Please fill all fields");
                return;
            }
            
            try {
                await createLearningGoal(title, description);
                document.getElementById("addGoalForm").classList.add("hidden");
                setupGoals();
            } catch (error) {
                showPopup("Error creating goal: " + error.message);
            }
        });
        
        document.getElementById("cancelGoalBtn").addEventListener("click", () => {
            document.getElementById("addGoalForm").classList.add("hidden");
        });
        
    } catch (error) {
        console.error("Error loading goals:", error);
        document.getElementById("goalsList").innerHTML = "<p>Error loading learning goals</p>";
    }
}

function setupChat() {
    const chatHistory = document.getElementById("chatHistory");
    const chatInput = document.getElementById("chatMessage");
    const sendButton = document.getElementById("sendChatBtn");

    const user = JSON.parse(sessionStorage.getItem("user"));
    const userId = user ? user.id || 'anonymous' : 'anonymous';
    
    const storedHistory = localStorage.getItem(`chatHistory_${userId}`);
    if (storedHistory) {
        chatHistory.innerHTML = storedHistory;
    }
    
    sendButton.addEventListener("click", async () => {
        const message = chatInput.value.trim();
        if (!message) return;
        
        chatHistory.innerHTML += `<div class="user-message fade-in">User: ${message}</div>`;
        chatInput.value = "";
        
        try {
            const response = await sendChatMessage(message);
            chatHistory.innerHTML += `<div class="ai-message fade-in">AI: ${response.response}</div>`;
            localStorage.setItem(`chatHistory_${userId}`, chatHistory.innerHTML);

            if (response.recommendation && response.recommendation.length > 0) {
                const recommendationsDiv = document.getElementById("careerRecommendations");
                const recommendationsList = document.getElementById("recommendationsList");
                
                recommendationsDiv.classList.remove("hidden");
                recommendationsList.innerHTML = response.recommendation.map((career, index) => `
                    <div class="career-recommendation fade-in">
                        <h4>${career.title} (${career.match_percentage}% Match)</h4>
                        <p>${career.description}</p>
                        <button class="select-career-btn" data-id="${index + 1}">Select This Career</button>
                    </div>
                `).join("");
                
                document.querySelectorAll(".select-career-btn").forEach(button => {
                    button.addEventListener("click", async () => {
                        const careerId = button.getAttribute("data-id");
                        try {
                            const result = await selectCareer(parseInt(careerId));
                            showPopup(result.message || "Career selected successfully!");
                            document.getElementById("btnGoals").click();
                        } catch (error) {
                            showPopup("Error selecting career: " + error.message);
                        }
                    });
                });
            }
            
        } catch (error) {
            chatHistory.innerHTML += `<div class="error-message fade-in">Error: ${error.message}</div>`;
        }
        
        chatHistory.scrollTop = chatHistory.scrollHeight;
    });
    
    chatInput.addEventListener("keypress", (event) => {
        if (event.key === "Enter") {
            sendButton.click();
        }
    });
}

async function setupCareer() {
    const careerPathDiv = document.getElementById("careerPath");
    
    try {
        const recommendations = await getCareerRecommendations();
        
        if (recommendations && recommendations.length > 0) {
            const selectedCareer = recommendations[0];
            
            careerPathDiv.innerHTML = `
                <div class="selected-career fade-in">
                    <h3>Your Chosen Path: ${selectedCareer.title}</h3>
                    <p>${selectedCareer.description}</p>
                    <div class="match-percentage">Match: ${selectedCareer.match_percentage}%</div>
                </div>
                <div class="learning-path fade-in">
                    <h3>Recommended Learning Path:</h3>
                    <ol>
                        <li>Learn ${selectedCareer.title} fundamentals</li>
                        <li>Complete basic courses</li>
                        <li>Gain project experience</li>
                        <li>Build a portfolio</li>
                        <li>Prepare for job interviews</li>
                    </ol>
                </div>
            `;
        } else {
            careerPathDiv.innerHTML = `
                <p>You haven't chosen a career path yet.</p>
                <p>Visit the AI Chat for career recommendations!</p>
                <button id="goToChatBtn" class="action-btn">Go to Chat</button>
            `;
            
            document.getElementById("goToChatBtn").addEventListener("click", () => {
                document.getElementById("btnChat").click();
            });
        }
    } catch (error) {
        console.error("Error loading career path:", error);
        careerPathDiv.innerHTML = "<p>No career path found</p>";
    }
}

// Initial page load
navigate(sessionStorage.getItem("token") ? "dashboard" : "login");

function showPopup(message) {
    const popup = document.createElement("div");
    popup.classList.add("popup", "fade-in");
    popup.innerHTML = `
        <div class="popup-content">
            <p>${message}</p>
            <button id="popupClose">OK</button>
        </div>
    `;
    document.body.appendChild(popup);

    document.getElementById("popupClose").addEventListener("click", () => {
        popup.classList.remove("fade-in");
        popup.classList.add("fade-out");
        setTimeout(() => popup.remove(), 300);
    });
}

// Error boundary handler
window.addEventListener("error", (event) => {
    showPopup("An unexpected error occurred: " + event.message);
});