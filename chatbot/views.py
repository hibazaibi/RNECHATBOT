import os
from django.shortcuts import render, redirect
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

MODEL = "llama3-8b-8192"
MAX_HISTORY_LENGTH = 5
MAX_TOKENS = 4000

def chatbot_view(request):
    # Initialize fresh session if needed
    if 'history' not in request.session:
        request.session['history'] = [{
            "role": "system",
            "content": (
                "Tu es un assistant administratif officiel du Registre National des Entreprises (RNE) en Tunisie. "
                "Tu fournis des informations précises et à jour sur :\n"
                "- Les procédures d'immatriculation des entreprises\n"
                "- Les documents requis pour chaque type de société\n"
                "- Les délais et coûts associés\n"
                "- Les démarches en ligne via le portail RNE\n"
                "- La législation tunisienne relative aux entreprises\n\n"
                "Sois concis et professionnel. Réponses courtes et précises."
            )
        }]
        request.session['last_message'] = None
        request.session.modified = True

    # Handle reset action
    if request.method == 'POST' and 'reset' in request.POST:
        request.session['history'] = [request.session['history'][0]]  # Keep only system message
        request.session['last_message'] = None
        request.session.modified = True
        return redirect('/')

    # Handle message submission
    if request.method == 'POST' and (message := request.POST.get("message")):
        # Prevent duplicate submission
        if message != request.session.get('last_message'):
            request.session['last_message'] = message
            request.session['history'].append({"role": "user", "content": message[:500]})

            try:
                # Truncate history if needed
                if len(request.session['history']) > 2 * MAX_HISTORY_LENGTH + 1:
                    request.session['history'] = (
                        [request.session['history'][0]] +
                        request.session['history'][-2 * MAX_HISTORY_LENGTH:]
                    )

                response = client.chat.completions.create(
                    messages=request.session['history'],
                    model=MODEL,
                    max_tokens=MAX_TOKENS
                )

                bot_reply = response.choices[0].message.content
                request.session['history'].append({"role": "assistant", "content": bot_reply})
                request.session.modified = True

            except Exception as e:
                request.session['history'].append({
                    "role": "assistant",
                    "content": f"Désolé, une erreur est survenue. Veuillez reformuler. ({str(e)})"
                })
                request.session.modified = True

    # Clear last_message flag on GET requests to allow new messages
    if request.method == 'GET':
        request.session['last_message'] = None
        request.session.modified = True

    return render(request, "chat.html", {
        "history": request.session.get('history', [])[1:],
        "conversation_too_long": len(request.session.get('history', [])) > 10,
        "current_path": request.path  # Add this line
    })

def rne_info(request):
    return render(request, "rne_info.html", {
        "current_path": request.path  # Add this line
    })
def contact_view(request):
    return render(request, "contact.html", {
        "current_path": request.path
    })
