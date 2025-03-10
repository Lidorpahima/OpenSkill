async function login(username, password) {
    try {
        const response = await fetch("http://localhost:8080/api/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password })
        });
        if (!response.ok) throw new Error("שגיאה בהתחברות");
        return await response.json();
    } catch (error) {
        return { success: false, message: error.message };
    }
}
