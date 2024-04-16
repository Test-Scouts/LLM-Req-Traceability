import torch
from transformers import pipeline, StoppingCriteriaList, StoppingCriteria
import dotenv
import os

dotenv.load_dotenv()

device = "cuda" if torch.cuda.is_available() else "cpu"
model_path = os.getenv("AI_SWE-MODEL_PATH")

# (Optional) - define a stopping criteria
# We ideally want the model to stop generate once the response from the Bot is generated
class StopOnTokenCriteria(StoppingCriteria):
    def __init__(self, stop_token_id):
        self.stop_token_id = stop_token_id

    def __call__(self, input_ids, scores, **kwargs):
        return input_ids[0, -1] == self.stop_token_id


pipe = pipeline(
    task="text-generation",
    model=model_path,
    device=device
)

stop_on_token_criteria = StopOnTokenCriteria(stop_token_id=pipe.tokenizer.bos_token_id)

def translate_to_swedish(text):
    # This will translate English to Swedish
    # To translate from Swedish to English the prompt would be:
    prompt = f"<|endoftext|><s>User: Översätt till Engelska från Svenska\n{text}<s>Bot:"

    #prompt = f"<|endoftext|><s>User: Översätt till Svenska från Engelska\n{text}<s>Bot:"

    input_tokens = pipe.tokenizer(prompt, return_tensors="pt").input_ids.to(device)
    max_model_length = 2048
    dynamic_max_length = max_model_length - input_tokens.shape[1]

    response = pipe(
        prompt,
        max_length=dynamic_max_length,
        truncation=True,
        stopping_criteria=StoppingCriteriaList([stop_on_token_criteria])
    )

    return response[0]["generated_text"].split("<s>Bot: ")[-1]



requirement = """
S1 - Lagkrav

Vid tidpunkten för kontraktsskrivande gällande Lagar, Föreskrifter och standarder med avseende på funktion och säkerhet ska (S1) uppfyllas för Mätsystemets alla delar enligt nedanstående punkter 1–13.
1. Ellag SFS 1997:857.
2. Förordningen (SFS 1999:716) om mätning, beräkning och rapportering av överförd el.
3. EIFS 2016:2 – Energimarknadsinspektionens Föreskrifter och allmänna råd om mätning, beräkning och rapportering av överförd el.
4. STAFS 2016:1 – Swedacs Föreskrifter om mätinstrument.
5. STAFS 2016:4 – Swedacs Föreskrifter och allmänna råd om mätare för aktiv elenergi.
6. STAFS 2009:8 – Swedacs Föreskrifter och allmänna råd om mätsystem för mätning av överförd el.
7. STAFS 2009:9 – Swedacs Föreskrifter och allmänna råd om återkommande kontroll av mätare för aktiv elenergi.
8. EU:s MID direktiv 2014/32/EU.
9. Utökat typgodkännande och certifiering av Kategori 1 och 2 mätare enligt metod SPM 1618, test med 12kV stötspänning.
10. Standarder: SS-EN61869-1, SS-EN61869-2, SS-EN50470 och IEC 62056 (DLMS/COSEM suite).
11. EU Förordning 2016/679 av den 27 april 2016 om skydd för fysiska personer med avseende på behandling av personuppgifter och om det fria flödet av sådana uppgifter och om upphävande av direktiv 95/46/EG (allmän dataskyddsförordning).
12. EU-försäkran om överenstämmelse ska finnas för Mätsystemet om detta eller delar därav tillverkas i land utanför EU.
13. Lag (2003:389) om elektronisk kommunikation.

"""
test_case = """
S257 - Ny nyckel/lösenord

Kamstrup visar på hur de uppfyller:
1. Ellag SFS 1997:857.
Kamstrup visar på hur de uppfyller:
2. Förordningen (SFS 1999:716) om mätning, beräkning och rapportering av överförd el.
Kamstrup visar på hur de uppfyller:
3. EIFS 2016:2 – Energimarknadsinspektionens Föreskrifter och allmänna råd om mätning, beräkning och rapportering av överförd el.
Kamstrup visar på hur de uppfyller:
4. STAFS 2016:1 – Swedacs Föreskrifter om mätinstrument.
Kamstrup visar på hur de uppfyller:
5. STAFS 2016:4 – Swedacs Föreskrifter och allmänna råd om mätare för aktiv elenergi.
Kamstrup visar på hur de uppfyller:
6. STAFS 2009:8 – Swedacs Föreskrifter och allmänna råd om mätsystem för mätning av överförd el.
Kamstrup visar på hur de uppfyller:
7. STAFS 2009:9 – Swedacs Föreskrifter och allmänna råd om återkommande kontroll av mätare för aktiv elenergi.
Kamstrup visar på hur de uppfyller:
8. EU:s MID direktiv 2014/32/EU.
Kamstrup visar på hur de uppfyller:
9. Utökat typgodkännande och certifiering av Kategori 1 och 2 mätare enligt metod SPM 1618, test med 12kV stötspänning.
Kamstrup visar på hur de uppfyller:
10. Standarder: SS-EN61869-1, SS-EN61869-2, SS-EN50470 och IEC 62056 (DLMS/COSEM suite).
Kamstrup visar på hur de uppfyller:
11. EU Förordning 2016/679 av den 27 april 2016 om skydd för fysiska personer med avseende på behandling av personuppgifter och om det fria flödet av sådana uppgifter och om upphävande av direktiv 95/46/EG (allmän dataskyddsförordning).
Kamstrup visar på hur de uppfyller:
12. EU-försäkran om överenstämmelse ska finnas för Mätsystemet om detta eller delar därav tillverkas i land utanför EU.
Kamstrup visar på hur de uppfyller:
13. Lag (2003:389) om elektronisk kommunikation.

"""

sp="\n\n"

print(translate_to_swedish(requirement))
print(sp)
print(translate_to_swedish(test_case))
