import os
from typing import Dict, List


class ModelWrapper:
    def __init__(self):
        self.pipeline = None
        self._init_model()

    def _init_model(self):
        model_id = os.environ.get(
            "K_SASA_MODEL_ID", "meta-llama/Meta-Llama-3.1-8B-Instruct"
        )
        load_4bit = os.environ.get("K_SASA_LOAD_4BIT", "1") == "1"
        try:
            import transformers  # type: ignore
            from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline  # type: ignore
            kwargs = {}
            if load_4bit:
                try:
                    import bitsandbytes  # noqa: F401

                    kwargs.update(
                        {
                            "device_map": "auto",
                            "load_in_4bit": True,
                            "bnb_4bit_compute_dtype": "bfloat16",
                            "bnb_4bit_use_double_quant": True,
                            "bnb_4bit_quant_type": "nf4",
                        }
                    )
                except Exception:
                    pass

            tok = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
            mdl = AutoModelForCausalLM.from_pretrained(
                model_id, trust_remote_code=True, **kwargs
            )
            self.pipeline = pipeline(
                "text-generation",
                model=mdl,
                tokenizer=tok,
                max_new_tokens=600,
                do_sample=True,
                temperature=0.6,
                top_p=0.9,
            )
        except Exception:
            self.pipeline = None

    def _fallback_plan(self, context: Dict) -> str:
        grade = context.get("grade", "").__str__()
        subject = context.get("subject", "Somo")
        duration = context.get("duration_minutes", 30)
        return (
            f"Mpango wa Somo ({subject}) — Darasa la {grade} — Dakika {duration}\n"
            "Malengo ya Kujifunza:\n"
            "- Mwanafunzi ataweza ...\n"
            "Vifaa/Vitendea Kazi:\n"
            "- Ubao, kalamu, karatasi (au vifaa vinavyofaa)\n"
            "Shughuli kwa Mgawanyo wa Muda:\n"
            "- Dakika 0-5: Utangulizi na uanzishaji wa maarifa ya awali\n"
            "- Dakika 5-20: Shughuli kuu kwa vikundi/vinafsi\n"
            "- Dakika 20-28: Majumuisho na mazoezi ya haraka\n"
            "- Dakika 28-30: Tathmini fupi na kazi ya nyumbani\n"
            "Tathmini:\n"
            "- Maswali mafupi ya kukagua ufahamu\n"
        )

    def generate_lesson_plan(self, context: Dict, evidence: List[Dict]) -> str:
        language = (context.get("language", "sw") or "sw").lower()
        subject = context.get("subject", "Somo")
        grade = context.get("grade", "").__str__()
        duration = context.get("duration_minutes", 30)

        if self.pipeline is None:
            return self._fallback_plan(context)

        evidence_text = "\n".join(
            [f"- Chanzo: {c.get('source')} | Dondoo: {c.get('snippet')}" for c in evidence][:6]
        )
        system_sw = (
            "Wewe ni msaidizi wa elimu unayetengeneza mpango wa somo wa dakika 30 kwa shule ya msingi kwa Kiswahili."
            " Zingatia malengo ya kujifunza, vifaa, shughuli zenye mgawanyo wa muda, na tathmini."
            " Hakikisha mpango ni salama na unafaa umri."
        )
        user_sw = (
            f"Tengeneza mpango wa somo wa dakika {duration} kwa '{subject}', Darasa la {grade}.\n"
            f"Ushahidi (RAG):\n{evidence_text}\n"
            "Jibu kwa muundo: Malengo ya Kujifunza, Vifaa, Shughuli (kwa mgawanyo wa muda), Tathmini."
        )
        prompt = f"<s>[SYSTEM]\n{system_sw}\n[/SYSTEM]\n[USER]\n{user_sw}\n[/USER]\n[ASSISTANT]"
        out = self.pipeline(prompt)
        text = out[0]["generated_text"]
        # naive post-process: get assistant continuation
        if "[ASSISTANT]" in text:
            text = text.split("[ASSISTANT]")[-1].strip()
        return text
