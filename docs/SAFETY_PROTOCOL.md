# Safety Protocol Documentation

## 1. Guiding Principle

The absolute highest priority of the **OMANI-Therapist-Voice ("Elile")** system is the safety and well-being of the user. The application is designed as a supportive listening tool and is not a substitute for professional medical care. In any situation where a user expresses intent for self-harm or harm to others, the system is programmed to immediately de-escalate and refer the user to professional, urgent help.

## 2. Trigger Mechanism

The safety protocol is activated through instruction-based intent detection within the primary LLM (GPT-4o). The system prompt contains a non-negotiable, high-priority rule that instructs the AI to constantly monitor user input for keywords and phrases related to:
-   Suicide or suicidal ideation.
-   Self-harm.
-   Harming others.
-   Severe, unmanageable distress indicating a crisis.

This logic is embedded directly within the `backend/prompts.py` file to ensure it is present in every single API call to the response generation model.

## 3. Escalation Protocol: The Safety Response

Upon detection of a crisis trigger, the AI is instructed to **immediately and unconditionally** interrupt the standard conversational flow. It will not attempt to counsel the user through the crisis. Instead, it will deliver a pre-defined, empathetic, and direct safety response.

### The Mandated AI Response

The system prompt explicitly defines the required response. The AI must deliver the following message, translated into a clear and supportive Omani Arabic tone:

> **Original English Instruction:** "It sounds like you are going through a very difficult time, and it's brave of you to share this. It's really important to talk to someone who can help you right away. Please reach out to the national mental health support line in Oman at [Placeholder for Omani Crisis Line Number]. They are available to help you."

> **Example Arabic Implementation:** "واضح إنك تمر بوقت صعب جداً، وشجاعة منك إنك تشارك هذا الشعور. من المهم جداً إنك تتكلم مع شخص يقدر يساعدك فوراً. رجاءً تواصل مع خط الدعم النفسي الوطني في عُمان على الرقم [يتم وضع رقم خط الأزمات في عُمان هنا]. هم موجودين لمساعدتك."

*(Note: A placeholder number is used. In a real-world application, this would be the official, verified crisis line number for Oman.)*

## 4. Data Handling and Reporting

In a production environment, any session where the safety protocol is triggered would be flagged in the database. This would allow for anonymized statistical analysis to understand the frequency of crisis events and could be configured to notify a human supervision team for review, in accordance with privacy laws like HIPAA and local data protection regulations. The current implementation logs the conversation but does not include an automated flagging or notification system.