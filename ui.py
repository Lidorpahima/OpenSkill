import streamlit as st
import requests

st.title("📚 UPSKILL - מערכת למידה מותאמת אישית")

st.sidebar.header("🔑 התחברות")
email = st.sidebar.text_input("אימייל")
password = st.sidebar.text_input("סיסמה", type="password")

if st.sidebar.button("🔓 התחבר"):
    with st.spinner("מתחבר..."):
        response = requests.post(
            "http://localhost:8080/auth/login",
            json={"email": email, "password": password}
        )
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            st.session_state["token"] = token
            st.sidebar.success("✅ התחברות מוצלחת!")
        else:
            st.sidebar.error("❌ אימייל או סיסמה שגויים")

if "token" in st.session_state:
    st.success("🔓 אתה מחובר בהצלחה!")

    if st.button("📢 בקש המלצות קריירה"):
        headers = {"Authorization": f"Bearer {st.session_state['token']}"}
        response = requests.get("http://localhost:8080/ai_chat/career_recommendations/", headers=headers)

        if response.status_code == 200:
            careers = response.json()
            st.write("🎯 **המלצות קריירה:**")
            for career in careers:
                st.write(f"🔹 **{career['title']}** - {career['description']} (התאמה: {career['match_percentage']}%)")
        else:
            st.error("⚠️ אין המלצות זמינות כרגע.")
