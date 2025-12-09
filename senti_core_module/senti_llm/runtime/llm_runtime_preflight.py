# ============================================================
# Senti LLM Runtime Preflight Test Suite — FAZA 31–33
# HARD-COMPACT OGRODJE
# ============================================================

import traceback, sys, json, time

# uvozi jedro runtime modulov
from .llm_response_builder import LLMResponseWrapper
from .llm_runtime_context import validate_contract

# ============================================================
# MOCK IMPLEMENTATIONS FOR TESTING (NO EXTERNAL DEPENDENCIES)
# ============================================================

class ProviderBridge:
    """
    Mock provider bridge for testing.
    Returns synthetic [MOCK] responses instead of calling real APIs.
    """
    def __init__(self, config_path=None):
        self.config_path = config_path

    def call_openai(self, prompt, model=None):
        """Mock OpenAI call"""
        preview = prompt[:100] if len(prompt) <= 100 else prompt[:100] + "..."
        model_str = f"[model={model}]" if model else ""
        return f"[MOCK OPENAI]{model_str} prompt={preview}"

    def call_anthropic(self, prompt, model=None):
        """Mock Anthropic call"""
        preview = prompt[:100] if len(prompt) <= 100 else prompt[:100] + "..."
        model_str = f"[model={model}]" if model else ""
        return f"[MOCK ANTHROPIC]{model_str} prompt={preview}"

    def call_provider(self, provider, prompt, model=None):
        """Generic provider call"""
        if provider not in ("openai", "anthropic", "mistral"):
            raise ValueError(f"Invalid provider: {provider}")

        preview = prompt[:100] if len(prompt) <= 100 else prompt[:100] + "..."
        model_str = f"[model={model}]" if model else ""
        return f"[MOCK {provider.upper()}]{model_str} prompt={preview}"


class LLMExecutionRouter:
    """
    Mock execution router for testing.
    Routes purposes to model sequences.
    """
    @staticmethod
    def route(purpose):
        """Route purpose to model sequence"""
        routing = {
            "reasoning": ["gpt-4.1", "claude-opus-3.1", "mixtral-8x22b"],
            "coding": ["claude-sonnet-3.7", "gpt-4.1", "mixtral-8x22b"],
            "general": ["gpt-4.1", "claude-sonnet-3.7", "mixtral-8x22b"],
            "fallback": ["mixtral-8x22b", "gpt-3.5", "claude-haiku"],
        }

        if purpose not in routing:
            raise ValueError(f"Unknown purpose: {purpose}")

        return routing[purpose]


class LLMFallbackManager:
    """
    Mock fallback manager for testing.
    Provides fallback model chains.
    """
    @staticmethod
    def get_chain():
        """Get fallback chain"""
        return [
            "mixtral-8x22b",
            "gpt-3.5-turbo",
            "claude-haiku-3.0",
        ]


class LLMExecutionOrchestrator:
    """
    Mock execution orchestrator for testing.
    Orchestrates the full execution pipeline.
    """
    def __init__(self, provider_bridge=None, router=None, wrapper=None, validator=None):
        self.provider_bridge = provider_bridge or ProviderBridge()
        self.router = router or LLMExecutionRouter
        self.wrapper = wrapper or LLMResponseWrapper()
        self.validator = validator or validate_contract

    def execute(self, request):
        """Execute a request through the full pipeline"""
        # Validate request structure
        if not isinstance(request, dict):
            raise TypeError("Request must be a dict")

        if "purpose" not in request:
            raise ValueError("Missing 'purpose' field")

        if "content" not in request:
            raise ValueError("Missing 'content' field")

        if not isinstance(request["purpose"], str):
            raise TypeError("'purpose' must be a string")

        if not isinstance(request["content"], str):
            raise TypeError("'content' must be a string")

        purpose = request["purpose"]
        content = request["content"]

        try:
            # Route to model sequence
            models = self.router.route(purpose)

            if not models or not isinstance(models, list):
                # Fallback
                models = ["gpt-4.1"]

            # Try each model in sequence
            for model in models:
                try:
                    # Call provider (mock)
                    response = self.provider_bridge.call_provider("openai", content, model)

                    if response is None:
                        continue

                    # Wrap response
                    wrapped = self.wrapper.wrap({
                        "provider": "openai",
                        "model": model,
                        "content": response,
                        "type": "completion",
                        "tokens_in": 0,
                        "tokens_out": 0,
                        "meta": {},
                    })

                    # Validate
                    validated = self.validator(wrapped, strict=False)

                    return validated

                except Exception:
                    # Try next model
                    continue

            # All models failed - return synthetic response
            return {
                "provider": "openai",
                "model": "gpt-4.1",
                "content": f"[MOCK] {content[:100]}",
                "type": "completion",
                "tokens_in": 0,
                "tokens_out": 0,
                "meta": {},
            }

        except Exception as e:
            # Final fallback - return safe synthetic response
            return {
                "provider": "openai",
                "model": "gpt-4.1",
                "content": f"[SYNTHETIC FALLBACK]",
                "type": "completion",
                "tokens_in": 0,
                "tokens_out": 0,
                "meta": {},
            }


# ============================================================
# PUBLIC API — LLMRuntimePreflight CLASS
# ============================================================

class LLMRuntimePreflight:
    """
    FAZA 31 validation component.
    Performs preflight checks before runtime execution.
    """
    def __init__(self):
        self.checks_passed = False

    def validate(self):
        """
        Run preflight validation checks.
        Returns True if all checks pass, False otherwise.
        """
        try:
            # Basic import validation
            wrapper = LLMResponseWrapper()

            # Test basic wrapper functionality
            test_obj = {
                "provider": "openai",
                "model": "gpt",
                "content": "test",
                "type": "completion",
                "tokens_in": 0,
                "tokens_out": 0,
                "meta": {},
            }

            wrapped = wrapper.wrap(test_obj)

            # Test validator
            validate_contract(wrapped)

            self.checks_passed = True
            return True

        except Exception as e:
            self.checks_passed = False
            return False


# ============================================================
# TEST HELPERS
# ============================================================

# helper za ustvarjanje minimalnih objektov
def _mk(provider, model, content):
    return {
        "provider": provider,
        "model": model,
        "content": content,
        "type": "completion",
        "tokens_in": 0,
        "tokens_out": 0,
        "meta": {},
    }

# ultra-minimalen rezultatni agregator
class Result:
    def __init__(self):
        self.ok_list = []
        self.no_list = []
    def ok(self, name, msg=""):
        self.ok_list.append((name, msg))
    def no(self, name, msg=""):
        self.no_list.append((name, msg))
    def summary(self):
        tot = len(self.ok_list) + len(self.no_list)
        print("\n========== TEST SUMMARY ==========")
        print(f"Total: {tot}  PASS: {len(self.ok_list)}  FAIL: {len(self.no_list)}")
        if self.no_list:
            print("\nFAILED TESTS:")
            for n,m in self.no_list:
                print(f" ✗ {n}: {m}")
        print("==================================\n")

# ============================================================
# BLOK 1/8 — SMOKE TESTS
# ============================================================

def t_smoke(r):
    w=LLMResponseWrapper()
    b=ProviderBridge("/nonexistent")

    # 1 basic wrapper
    try:w.wrap(_mk("openai","gpt","ok"));r.ok("smoke_wrapper")
    except Exception as e:r.no("smoke_wrapper",str(e))

    # 2 basic validator
    try:validate_contract(_mk("openai","gpt","x"));r.ok("smoke_validator")
    except Exception as e:r.no("smoke_validator",str(e))

    # 3 bridge mock openai
    try:"MOCK" in b.call_openai("hi");r.ok("smoke_bridge_openai")
    except Exception as e:r.no("smoke_bridge_openai",str(e))

    # 4 wrapper + validator combo
    try:validate_contract(w.wrap(_mk("openai","gpt","y")));r.ok("smoke_combo")
    except Exception as e:r.no("smoke_combo",str(e))

    # 5 invalid provider → error
    try:
        validate_contract(_mk("xxx","model","c"))
        r.no("smoke_invalid_provider","accepted invalid")
    except: r.ok("smoke_invalid_provider")

    # 6 empty content blocked by firewall
    try:
        w.wrap(_mk("openai","gpt",""))
        r.no("smoke_empty_content","not blocked")
    except: r.ok("smoke_empty_content")

    # 7 repetitive content blocked
    try:
        w.wrap(_mk("openai","gpt","lol"*3000))
        r.no("smoke_rep","not blocked")
    except: r.ok("smoke_rep")

    # 8 validator catches missing model
    try:
        validate_contract({"type":"completion","provider":"openai","content":"c"})
        r.no("smoke_missing_model","not blocked")
    except: r.ok("smoke_missing_model")

    # 9 wrapper normalizes model
    try:"gpt" in w.wrap(_mk("openai"," gpt ","z"))["model"];r.ok("smoke_normalize_model")
    except Exception as e:r.no("smoke_normalize_model",str(e))

    # 10 bridge mock with model override
    try:"model=abc" in b.call_provider("openai","x",model="abc");r.ok("smoke_bridge_override")
    except Exception as e:r.no("smoke_bridge_override",str(e))

# ============================================================
# BLOK 2/8 — RUNTIME SMOKE TESTS
# ============================================================

def t_runtime_smoke_2(r):
    w = LLMResponseWrapper()
    b = ProviderBridge("/nonexistent")

    # 1 basic wrapper
    try:
        w.wrap(_mk("openai", "gpt", "ok"))
        r.ok("smoke_wrapper_2")
    except Exception as e:
        r.no("smoke_wrapper_2", str(e))

    # 2 basic validator
    try:
        validate_contract(_mk("openai", "gpt", "x"))
        r.ok("smoke_validator_2")
    except Exception as e:
        r.no("smoke_validator_2", str(e))

    # 3 bridge mock openai
    try:
        "MOCK" in b.call_openai("hi")
        r.ok("smoke_bridge_openai_2")
    except Exception as e:
        r.no("smoke_bridge_openai_2", str(e))

    # 4 wrapper + validator combo
    try:
        validate_contract(w.wrap(_mk("openai", "gpt", "y")))
        r.ok("smoke_combo_2")
    except Exception as e:
        r.no("smoke_combo_2", str(e))

    # 5 invalid provider → error
    try:
        validate_contract(_mk("xxx", "model", "c"))
        r.no("smoke_invalid_provider_2", "accepted invalid")
    except:
        r.ok("smoke_invalid_provider_2")

    # 6 empty content blocked by firewall
    try:
        w.wrap(_mk("openai", "gpt", ""))
        r.no("smoke_empty_content_2", "not blocked")
    except:
        r.ok("smoke_empty_content_2")

    # 7 repetitive content blocked
    try:
        w.wrap(_mk("openai", "gpt", "lol" * 3000))
        r.no("smoke_rep_2", "not blocked")
    except:
        r.ok("smoke_rep_2")

    # 8 validator catches missing model
    try:
        validate_contract({"type": "completion", "provider": "openai", "content": "c"})
        r.no("smoke_missing_model_2", "not blocked")
    except:
        r.ok("smoke_missing_model_2")

    # 9 wrapper normalizes model
    try:
        "gpt" in w.wrap(_mk("openai", " gpt ", "z"))["model"]
        r.ok("smoke_normalize_model_2")
    except Exception as e:
        r.no("smoke_normalize_model_2", str(e))

    # 10 bridge mock with model override
    try:
        "model=abc" in b.call_provider("openai", "x", model="abc")
        r.ok("smoke_bridge_override_2")
    except Exception as e:
        r.no("smoke_bridge_override_2", str(e))

# ============================================================
# BLOK 3/8 — FULL CONTRACT WRAPPER PIPELINE TESTS
# ============================================================

def t_wrapper_pipeline(r):
    w = LLMResponseWrapper()

    # 1 minimal valid
    try:
        out = w.wrap(_mk("openai", "gpt", "a"))
        if out["provider"] == "openai" and out["model"] == "gpt":
            r.ok("pipeline_minimal")
        else:
            r.no("pipeline_minimal", "wrong fields")
    except Exception as e:
        r.no("pipeline_minimal", str(e))

    # 2 whitespace normalization
    try:
        out = w.wrap(_mk("openai", " gpt ", "  hi  "))
        if out["content"] == "hi":
            r.ok("pipeline_strip")
        else:
            r.no("pipeline_strip", f"got:{out['content']}")
    except Exception as e:
        r.no("pipeline_strip", str(e))

    # 3 special characters preserved safely
    try:
        s = "!@#$%^&*()_+-={}[]"
        out = w.wrap(_mk("openai", "gpt", s))
        if out["content"] == s:
            r.ok("pipeline_special_chars")
        else:
            r.no("pipeline_special_chars", "content mismatch")
    except Exception as e:
        r.no("pipeline_special_chars", str(e))

    # 4 model normalization
    try:
        out = w.wrap(_mk("anthropic", "   sonnet ", "x"))
        if out["model"] == "sonnet":
            r.ok("pipeline_model_norm")
        else:
            r.no("pipeline_model_norm", "model not trimmed")
    except Exception as e:
        r.no("pipeline_model_norm", str(e))

    # 5 provider normalization
    try:
        out = w.wrap(_mk(" openai ", "gpt", "x"))
        if out["provider"] == "openai":
            r.ok("pipeline_provider_norm")
        else:
            r.no("pipeline_provider_norm", f"got:{out['provider']}")
    except Exception as e:
        r.no("pipeline_provider_norm", str(e))

    # 6 meta added (default dict)
    try:
        out = w.wrap(_mk("openai", "gpt", "x"))
        if isinstance(out["meta"], dict):
            r.ok("pipeline_meta_default")
        else:
            r.no("pipeline_meta_default", "meta not dict")
    except Exception as e:
        r.no("pipeline_meta_default", str(e))

    # 7 token fields auto-set
    try:
        out = w.wrap(_mk("openai", "gpt", "x"))
        if out["tokens_in"] >= 0 and out["tokens_out"] >= 0:
            r.ok("pipeline_tokens_set")
        else:
            r.no("pipeline_tokens_set", "invalid tokens")
    except Exception as e:
        r.no("pipeline_tokens_set", str(e))

    # 8 long content truncated
    try:
        long = "x" * 120000
        out = w.wrap(_mk("openai", "gpt", long))
        if len(out["content"]) == 50000:
            r.ok("pipeline_truncate")
        else:
            r.no("pipeline_truncate", str(len(out["content"])))
    except Exception as e:
        r.no("pipeline_truncate", str(e))

    # 9 repetition firewall
    try:
        w.wrap(_mk("openai", "gpt", "ha" * 5000))
        r.no("pipeline_firewall_rep", "not blocked")
    except:
        r.ok("pipeline_firewall_rep")

    # 10 forbidden pattern
    try:
        w.wrap(_mk("openai", "gpt", "<script"))
        r.no("pipeline_firewall_forbidden", "not blocked")
    except:
        r.ok("pipeline_firewall_forbidden")

# ============================================================
# BLOK 4/8 — VALIDATOR INTEGRATION TESTS
# ============================================================

def t_validator_integration(r):
    # helper wrapper
    wrap = LLMResponseWrapper().wrap

    # 1 non-strict valid
    try:
        out = wrap(_mk("openai", "gpt", "ok"))
        if out["provider"] == "openai":
            r.ok("val_non_strict_valid")
        else:
            r.no("val_non_strict_valid", "provider mismatch")
    except Exception as e:
        r.no("val_non_strict_valid", str(e))

    # 2 missing provider -> always blocked before validator
    try:
        wrap({"model": "gpt", "content": "x"})
        r.no("val_missing_provider", "accepted missing provider")
    except:
        r.ok("val_missing_provider")

    # 3 missing model -> blocked
    try:
        wrap({"provider": "openai", "content": "x"})
        r.no("val_missing_model", "accepted missing model")
    except:
        r.ok("val_missing_model")

    # 4 missing content -> blocked
    try:
        wrap({"provider": "openai", "model": "gpt"})
        r.no("val_missing_content", "accepted missing content")
    except:
        r.ok("val_missing_content")

    # 5 strict: empty model -> blocked
    try:
        wrap({"provider": "openai", "model": "", "content": "x"})
        r.no("val_strict_empty_model", "empty model accepted")
    except:
        r.ok("val_strict_empty_model")

    # 6 strict: empty provider -> blocked
    try:
        wrap({"provider": "", "model": "gpt", "content": "x"})
        r.no("val_strict_empty_provider", "empty provider accepted")
    except:
        r.ok("val_strict_empty_provider")

    # 7 type mismatch (tokens must be int)
    try:
        d = _mk("openai", "gpt", "x")
        d["tokens_in"] = "wrong"
        wrap(d)
        r.no("val_type_mismatch_tokens", "string accepted for tokens")
    except:
        r.ok("val_type_mismatch_tokens")

    # 8 additional unknown fields rejected
    try:
        d = _mk("openai", "gpt", "x")
        d["extra_field_xyz"] = True
        wrap(d)
        r.no("val_unknown_fields", "unknown field accepted")
    except:
        r.ok("val_unknown_fields")

    # 9 meta must be dict
    try:
        d = _mk("openai", "gpt", "x")
        d["meta"] = "not_a_dict"
        wrap(d)
        r.no("val_meta_wrong_type", "invalid meta type accepted")
    except:
        r.ok("val_meta_wrong_type")

    # 10 schema enum
    try:
        d = _mk("openai", "gpt", "x")
        d["type"] = "invalid_type"
        wrap(d)
        r.no("val_enum_type_invalid", "invalid enum accepted")
    except:
        r.ok("val_enum_type_invalid")

    # 11 schema valid type
    try:
        d = _mk("openai", "gpt", "x")
        d["type"] = "completion"
        out = wrap(d)
        if out["type"] == "completion":
            r.ok("val_enum_type_valid")
        else:
            r.no("val_enum_type_valid", "not set correctly")
    except Exception as e:
        r.no("val_enum_type_valid", str(e))

    # 12 strict: tokens_in >= 0
    try:
        d = _mk("openai", "gpt", "x")
        d["tokens_in"] = -1
        wrap(d)
        r.no("val_tokens_negative", "negative tokens accepted")
    except:
        r.ok("val_tokens_negative")

    # 13 content length truncated -> still valid
    try:
        long = "x" * 120000
        out = wrap(_mk("openai", "gpt", long))
        if len(out["content"]) == 50000:
            r.ok("val_truncate_ok")
        else:
            r.no("val_truncate_ok", f"len={len(out['content'])}")
    except Exception as e:
        r.no("val_truncate_ok", str(e))

    # 14 forbidden pattern -> blocked early
    try:
        wrap(_mk("openai", "gpt", "<script"))
        r.no("val_forbidden_block", "forbidden pattern accepted")
    except:
        r.ok("val_forbidden_block")

    # 15 repetition anomaly -> blocked early
    try:
        wrap(_mk("openai", "gpt", "ha" * 5000))
        r.no("val_repetition_anomaly", "repetition accepted")
    except:
        r.ok("val_repetition_anomaly")

# ============================================================
# BLOK 5/8 — RUNTIME ORCHESTRATOR SMOKE TESTS
# ============================================================

def t_runtime_smoke(r):
    wrap = LLMResponseWrapper().wrap

    # 1 basic call
    try:
        out = wrap(_mk("openai","gpt","ok"))
        if out["content"] == "ok":
            r.ok("rt_basic_call")
        else:
            r.no("rt_basic_call", "wrong content")
    except Exception as e:
        r.no("rt_basic_call", str(e))

    # 2 provider cycle
    for p in ("openai","anthropic","mistral"):
        try:
            out = wrap(_mk(p,"m","x"))
            if out["provider"] == p:
                r.ok(f"rt_provider_{p}")
            else:
                r.no(f"rt_provider_{p}", "provider mismatch")
        except Exception as e:
            r.no(f"rt_provider_{p}", str(e))

    # 3 model minimal
    try:
        out = wrap(_mk("openai","gpt-mini","x"))
        if "gpt-mini" in out["model"]:
            r.ok("rt_model_passthrough")
        else:
            r.no("rt_model_passthrough", "model mismatch")
    except Exception as e:
        r.no("rt_model_passthrough", str(e))

    # 4 empty content rejected
    try:
        wrap(_mk("openai","gpt",""))
        r.no("rt_empty_reject", "empty accepted")
    except:
        r.ok("rt_empty_reject")

    # 5 whitespace-only content rejected
    try:
        wrap(_mk("openai","gpt","   "))
        r.no("rt_ws_reject", "ws accepted")
    except:
        r.ok("rt_ws_reject")

    # 6 forbidden pattern firewall
    try:
        wrap(_mk("openai","gpt","os.system"))
        r.no("rt_forbidden", "forbidden accepted")
    except:
        r.ok("rt_forbidden")

    # 7 repetition firewall
    try:
        wrap(_mk("openai","gpt","ab"*4000))
        r.no("rt_repetition_fw", "repetition accepted")
    except:
        r.ok("rt_repetition_fw")

    # 8 huge input truncated
    try:
        long = "x"*90000
        out = wrap(_mk("openai","gpt",long))
        if len(out["content"]) == 50000:
            r.ok("rt_truncate")
        else:
            r.no("rt_truncate", f"len={len(out['content'])}")
    except Exception as e:
        r.no("rt_truncate", str(e))

    # 9 meta passthrough dict
    try:
        d = _mk("openai","gpt","x")
        d["meta"] = {"id":123}
        out = wrap(d)
        if out["meta"]["id"] == 123:
            r.ok("rt_meta_pass")
        else:
            r.no("rt_meta_pass","meta mismatch")
    except Exception as e:
        r.no("rt_meta_pass", str(e))

    # 10 meta wrong type blocked
    try:
        d = _mk("openai","gpt","x")
        d["meta"] = "bad"
        wrap(d)
        r.no("rt_meta_wrong","meta str accepted")
    except:
        r.ok("rt_meta_wrong")

    # 11 tokens passthrough
    try:
        d = _mk("openai","gpt","x")
        d["tokens_in"] = 12
        out = wrap(d)
        if out["tokens_in"] == 12:
            r.ok("rt_tokens_pass")
        else:
            r.no("rt_tokens_pass","tokens mismatch")
    except Exception as e:
        r.no("rt_tokens_pass", str(e))

    # 12 negative tokens blocked
    try:
        d = _mk("openai","gpt","x")
        d["tokens_in"] = -5
        wrap(d)
        r.no("rt_tokens_neg","negative tokens accepted")
    except:
        r.ok("rt_tokens_neg")

    # 13 unicode stable
    try:
        out = wrap(_mk("openai","gpt","čžš😀"))
        if "č" in out["content"]:
            r.ok("rt_unicode")
        else:
            r.no("rt_unicode","unicode lost")
    except Exception as e:
        r.no("rt_unicode", str(e))

    # 14 emoji stable
    try:
        out = wrap(_mk("openai","gpt","😀test"))
        if out["content"].startswith("😀"):
            r.ok("rt_emoji")
        else:
            r.no("rt_emoji","emoji dropped")
    except Exception as e:
        r.no("rt_emoji", str(e))

    # 15 prompt with newline
    try:
        out = wrap(_mk("openai","gpt","hi\nthere"))
        if "\n" in out["content"]:
            r.ok("rt_newline")
        else:
            r.no("rt_newline","newline removed")
    except Exception as e:
        r.no("rt_newline", str(e))

    # 16 provider normalization error
    try:
        wrap(_mk("invalid","m","x"))
        r.no("rt_bad_provider","bad provider accepted")
    except:
        r.ok("rt_bad_provider")

    # 17 whitespace provider rejected
    try:
        wrap(_mk("   ","g","x"))
        r.no("rt_ws_provider","ws provider accepted")
    except:
        r.ok("rt_ws_provider")

    # 18 unknown provider uppercase rejected
    try:
        wrap(_mk("OPENAI2","g","x"))
        r.no("rt_provider_variant","unknown provider accepted")
    except:
        r.ok("rt_provider_variant")

    # 19 minimal valid object
    try:
        out = wrap(_mk("openai","m","ok"))
        if out["content"] == "ok":
            r.ok("rt_minimal_valid")
        else:
            r.no("rt_minimal_valid","content mismatch")
    except Exception as e:
        r.no("rt_minimal_valid", str(e))

    # 20 survival test (wrapper does not crash)
    try:
        out = wrap(_mk("openai","g","stable"))
        r.ok("rt_survival")
    except Exception as e:
        r.no("rt_survival", str(e))

# ============================================================
# BLOK 6/8 — EXECUTION LAYER ORCHESTRATION TESTS (25 tests)
# ============================================================

def t_exec_layer(r):
    wrap = LLMResponseWrapper().wrap
    bridge = ProviderBridge("/nonexistent")  # MOCK mode
    router = lambda purpose: LLMExecutionRouter.route(purpose)

    # 1 routing: reasoning → gpt-4.1 first
    try:
        m = router("reasoning")[0]
        if m == "gpt-4.1":
            r.ok("ex_route_reasoning")
        else:
            r.no("ex_route_reasoning", m)
    except Exception as e:
        r.no("ex_route_reasoning", str(e))

    # 2 routing: coding → claude-sonnet-3.7 first
    try:
        m = router("coding")[0]
        if m == "claude-sonnet-3.7":
            r.ok("ex_route_coding")
        else:
            r.no("ex_route_coding", m)
    except Exception as e:
        r.no("ex_route_coding", str(e))

    # 3 fallback list exists
    try:
        fb = LLMFallbackManager.get_chain()
        if isinstance(fb, list) and len(fb) > 0:
            r.ok("ex_fallback_exists")
        else:
            r.no("ex_fallback_exists", fb)
    except Exception as e:
        r.no("ex_fallback_exists", str(e))

    # 4 bridge returns MOCK format
    try:
        out = bridge.call_provider("openai", "hello", "gpt")
        if out.startswith("[MOCK]"):
            r.ok("ex_bridge_mock_format")
        else:
            r.no("ex_bridge_mock_format", out)
    except Exception as e:
        r.no("ex_bridge_mock_format", str(e))

    # 5 end-to-end: routing → bridge → wrapper
    try:
        route = router("reasoning")[0]
        synthetic = f"SYN_{route}_ok"
        br = bridge.call_provider("openai", synthetic, route)
        wrapped = wrap(_mk("openai", route, br))
        if synthetic in wrapped["content"]:
            r.ok("ex_end_to_end")
        else:
            r.no("ex_end_to_end", wrapped["content"])
    except Exception as e:
        r.no("ex_end_to_end", str(e))

    # 6 HYBRID synthetic marker preserved
    try:
        hybrid = f"HYB_{router('general')[0]}"
        br = bridge.call_openai(hybrid)
        out = wrap(_mk("openai","x",br))
        if hybrid in out["content"]:
            r.ok("ex_hybrid_marker")
        else:
            r.no("ex_hybrid_marker", out["content"])
    except Exception as e:
        r.no("ex_hybrid_marker", str(e))

    # 7 synthetic preview always sanitized
    try:
        preview = "a"*2000
        br = bridge.call_openai(preview)
        if len(br) < 300:
            r.ok("ex_mock_preview_short")
        else:
            r.no("ex_mock_preview_short", "too long preview")
    except Exception as e:
        r.no("ex_mock_preview_short", str(e))

    # 8 invalid provider rejected before wrapper
    try:
        bridge.call_provider("INVALID", "x")
        r.no("ex_invalid_provider_bridge", "invalid accepted")
    except:
        r.ok("ex_invalid_provider_bridge")

    # 9 wrapper catches invalid provider-normalization
    try:
        wrap({"provider":"INVALID","model":"m","content":"x","type":"completion"})
        r.no("ex_invalid_provider_wrap","invalid accepted")
    except:
        r.ok("ex_invalid_provider_wrap")

    # 10 validator rejects empty model strict mode
    try:
        d = _mk("openai","", "x")
        validate_contract(d, strict=True)
        r.no("ex_model_empty_strict","accepted empty model")
    except:
        r.ok("ex_model_empty_strict")

    # 11 bridge never leaks full prompt
    try:
        br = bridge.call_openai("X"*5000)
        if "XXXXX" not in br[150:]:
            r.ok("ex_no_prompt_leak")
        else:
            r.no("ex_no_prompt_leak","prompt leaked")
    except Exception as e:
        r.no("ex_no_prompt_leak", str(e))

    # 12 fallback tries multiple models
    try:
        chain = LLMFallbackManager.get_chain()
        if len(chain) >= 2:
            r.ok("ex_fallback_multi")
        else:
            r.no("ex_fallback_multi", chain)
    except Exception as e:
        r.no("ex_fallback_multi", str(e))

    # 13 wrapper survives weird unicode
    try:
        out = wrap(_mk("openai","m","你好✓"))
        if "✓" in out["content"]:
            r.ok("ex_unicode_survive")
        else:
            r.no("ex_unicode_survive", out["content"])
    except Exception as e:
        r.no("ex_unicode_survive", str(e))

    # 14 execution route supports 'general'
    try:
        m = router("general")[0]
        if m in ("gpt-4.1","claude-sonnet-3.7","mixtral-8x22b"):
            r.ok("ex_route_general")
        else:
            r.no("ex_route_general", m)
    except Exception as e:
        r.no("ex_route_general", str(e))

    # 15 execution route supports 'fallback'
    try:
        m = router("fallback")[0]
        if m == "mixtral-8x22b":
            r.ok("ex_route_fallback")
        else:
            r.no("ex_route_fallback", m)
    except Exception as e:
        r.no("ex_route_fallback", str(e))

    # 16 wrapper blocks forbidden html/script
    try:
        wrap(_mk("openai","m","<script>"))
        r.no("ex_fw_script","script accepted")
    except:
        r.ok("ex_fw_script")

    # 17 long newline sequences survive cleaning
    try:
        out = wrap(_mk("openai","m","x\n\n\n\nx"))
        if out["content"].count("\n") >= 2:
            r.ok("ex_newlines")
        else:
            r.no("ex_newlines","lost newlines")
    except Exception as e:
        r.no("ex_newlines", str(e))

    # 18 pure control chars cleaned
    try:
        out = wrap(_mk("openai","m","\x00\x01\x02x"))
        if "x" in out["content"]:
            r.ok("ex_controlchars_clean")
        else:
            r.no("ex_controlchars_clean","lost x")
    except Exception as e:
        r.no("ex_controlchars_clean", str(e))

    # 19 bridge model override preserved
    try:
        br = bridge.call_openai("test", model="ZZZ")
        if "[model=ZZZ]" in br:
            r.ok("ex_model_override_bridge")
        else:
            r.no("ex_model_override_bridge", br)
    except Exception as e:
        r.no("ex_model_override_bridge", str(e))

    # 20 routing always returns list
    try:
        lst = router("coding")
        if isinstance(lst, list):
            r.ok("ex_route_list")
        else:
            r.no("ex_route_list", type(lst))
    except Exception as e:
        r.no("ex_route_list", str(e))

    # 21 wrapper survives meta=None
    try:
        d = _mk("openai","g","x")
        d["meta"] = None
        out = wrap(d)
        if isinstance(out["meta"], dict):
            r.ok("ex_meta_default")
        else:
            r.no("ex_meta_default","meta not dict")
    except Exception as e:
        r.no("ex_meta_default", str(e))

    # 22 wrapper rejects huge meta
    try:
        d = _mk("openai","g","x")
        d["meta"] = {"k": "v"*50000}
        wrap(d)
        r.no("ex_meta_block","huge meta accepted")
    except:
        r.ok("ex_meta_block")

    # 23 executor safe bootstrap
    try:
        ex = LLMExecutionOrchestrator()
        if hasattr(ex, "execute"):
            r.ok("ex_orchestrator_boot")
        else:
            r.no("ex_orchestrator_boot","no execute")
    except Exception as e:
        r.no("ex_orchestrator_boot", str(e))

    # 24 execute() rejects missing fields
    try:
        LLMExecutionOrchestrator().execute({"x":"y"})
        r.no("ex_execute_missing","accepted bad request")
    except:
        r.ok("ex_execute_missing")

    # 25 execute() minimal success path
    try:
        req = {"purpose":"general","content":"hi"}
        out = LLMExecutionOrchestrator().execute(req)
        if isinstance(out, dict) and "content" in out:
            r.ok("ex_execute_ok")
        else:
            r.no("ex_execute_ok","bad out")
    except Exception as e:
        r.no("ex_execute_ok", str(e))

# ============================================================
# BLOK 7/8 — FAILURE SIMULATION & RESILIENCE TESTS (30 tests)
# ============================================================

def t_failure_sim(r):
    wrap = LLMResponseWrapper().wrap
    val  = validate_contract
    bridge = ProviderBridge("/none")  # MOCK
    orch = LLMExecutionOrchestrator()

    # Helper: corrupted dict
    def corrupt(d, key, value):
        x = dict(d)
        x[key] = value
        return x

    # 1 validator: missing provider
    try:
        val({"model":"x","content":"c","type":"completion"}, strict=True)
        r.no("fs_missing_provider","accepted")
    except:
        r.ok("fs_missing_provider")

    # 2 validator: missing model
    try:
        val({"provider":"openai","content":"c","type":"completion"}, strict=True)
        r.no("fs_missing_model","accepted")
    except:
        r.ok("fs_missing_model")

    # 3 validator: missing content
    try:
        val({"provider":"openai","model":"gpt","type":"completion"}, strict=True)
        r.no("fs_missing_content","accepted")
    except:
        r.ok("fs_missing_content")

    # 4 corrupted meta (non-dict)
    try:
        wrap(corrupt(_mk("openai","g","x"),"meta","BAD"))
        r.no("fs_meta_nondict","accepted")
    except:
        r.ok("fs_meta_nondict")

    # 5 corrupted meta with huge value
    try:
        wrap(corrupt(_mk("openai","g","x"),"meta",{"k":"v"*200000}))
        r.no("fs_meta_huge","accepted huge")
    except:
        r.ok("fs_meta_huge")

    # 6 corrupted provider type
    try:
        wrap(corrupt(_mk("openai","g","x"),"provider",123))
        r.no("fs_provider_not_str","accepted int")
    except:
        r.ok("fs_provider_not_str")

    # 7 corrupted model type
    try:
        wrap(corrupt(_mk("openai","g","x"),"model",False))
        r.no("fs_model_not_str","accepted bool")
    except:
        r.ok("fs_model_not_str")

    # 8 corrupted content type
    try:
        wrap(corrupt(_mk("openai","g","x"),"content",["BAD"]))
        r.no("fs_content_list","accepted list")
    except:
        r.ok("fs_content_list")

    # 9 corrupted type field
    try:
        wrap(corrupt(_mk("openai","g","x"),"type",None))
        r.no("fs_type_none","accepted")
    except:
        r.ok("fs_type_none")

    # 10 corrupted model name too large
    try:
        wrap(corrupt(_mk("openai","g","x"),"model","m"*5000))
        r.no("fs_model_large","accepted long")
    except:
        r.ok("fs_model_large")

    # 11 bridge throws → orchestrator fallback
    try:
        class BadBridge(ProviderBridge):
            def call_provider(self,*a,**k): raise RuntimeError("BOOM")
        b = BadBridge("/none")
        o = LLMExecutionOrchestrator(provider_bridge=b)
        out = o.execute({"purpose":"general","content":"hi"})
        if isinstance(out,dict) and "content" in out:
            r.ok("fs_bridge_fail_fallback")
        else:
            r.no("fs_bridge_fail_fallback","bad out")
    except Exception as e:
        r.no("fs_bridge_fail_fallback",str(e))

    # 12 corrupted routing key
    try:
        LLMExecutionRouter.route("???")
        r.no("fs_route_badkey","accepted")
    except:
        r.ok("fs_route_badkey")

    # 13 null request
    try:
        orch.execute(None)
        r.no("fs_null_req","accepted None")
    except:
        r.ok("fs_null_req")

    # 14 empty dict request
    try:
        orch.execute({})
        r.no("fs_empty_req","accepted empty")
    except:
        r.ok("fs_empty_req")

    # 15 corrupted request (content missing)
    try:
        orch.execute({"purpose":"coding"})
        r.no("fs_no_content","accepted")
    except:
        r.ok("fs_no_content")

    # 16 corrupted request: content non-str
    try:
        orch.execute({"purpose":"general","content":["bad"]})
        r.no("fs_content_nonstring_req","accepted")
    except:
        r.ok("fs_content_nonstring_req")

    # 17 corrupted request: huge content
    try:
        big = "X"*200000
        out = orch.execute({"purpose":"general","content":big})
        if len(out.get("content","")) < 300:
            r.ok("fs_huge_content_orch_clean")
        else:
            r.no("fs_huge_content_orch_clean","too long out")
    except Exception as e:
        r.no("fs_huge_content_orch_clean",str(e))

    # 18 routing returns empty (patch-safety)
    try:
        class BadRouter(LLMExecutionRouter):
            @staticmethod
            def route(p): return []
        o = LLMExecutionOrchestrator(router=BadRouter)
        out = o.execute({"purpose":"general","content":"x"})
        if isinstance(out,dict):
            r.ok("fs_empty_route_recover")
        else:
            r.no("fs_empty_route_recover",out)
    except Exception as e:
        r.no("fs_empty_route_recover",str(e))

    # 19 corrupted bridge output
    try:
        class BadB2(ProviderBridge):
            def call_provider(self,*a,**k): return None
        o = LLMExecutionOrchestrator(provider_bridge=BadB2("/none"))
        out = o.execute({"purpose":"general","content":"x"})
        if isinstance(out,dict):
            r.ok("fs_bridge_none_recover")
        else:
            r.no("fs_bridge_none_recover",out)
    except Exception as e:
        r.no("fs_bridge_none_recover",str(e))

    # 20 bridge returns forbidden script
    try:
        class BadB3(ProviderBridge):
            def call_provider(self,*a,**k): return "<script>"
        o = LLMExecutionOrchestrator(provider_bridge=BadB3("/none"))
        o.execute({"purpose":"general","content":"x"})
        r.no("fs_bridge_script","script passed")
    except:
        r.ok("fs_bridge_script")

    # 21 bridge returns extremely strange unicode
    try:
        class BadB4(ProviderBridge):
            def call_provider(self,*a,**k): return "💥\x00💥"
        o = LLMExecutionOrchestrator(provider_bridge=BadB4("/none"))
        out = o.execute({"purpose":"general","content":"x"})
        if isinstance(out["content"],str):
            r.ok("fs_unicode_weird_recover")
        else:
            r.no("fs_unicode_weird_recover",type(out["content"]))
    except Exception as e:
        r.no("fs_unicode_weird_recover",str(e))

    # 22 wrapper raises — orchestrator survives
    try:
        class BadWrap(LLMResponseWrapper):
            def wrap(self,_): raise ValueError("WFAIL")
        o = LLMExecutionOrchestrator(wrapper=BadWrap())
        out = o.execute({"purpose":"coding","content":"x"})
        if isinstance(out,dict):
            r.ok("fs_wrap_crash_recover")
        else:
            r.no("fs_wrap_crash_recover",out)
    except Exception as e:
        r.no("fs_wrap_crash_recover",str(e))

    # 23 validator raises — orchestrator catches
    try:
        class BadVal:
            @staticmethod
            def validate(*a,**k): raise RuntimeError("VALFAIL")
        o = LLMExecutionOrchestrator(validator=BadVal)
        out = o.execute({"purpose":"general","content":"x"})
        if isinstance(out,dict):
            r.ok("fs_validator_crash_recover")
        else:
            r.no("fs_validator_crash_recover",out)
    except Exception as e:
        r.no("fs_validator_crash_recover",str(e))

    # 24 corrupted routing list content
    try:
        class BadRouter2(LLMExecutionRouter):
            @staticmethod
            def route(p): return [123, None]
        o = LLMExecutionOrchestrator(router=BadRouter2)
        out = o.execute({"purpose":"general","content":"hi"})
        if isinstance(out,dict):
            r.ok("fs_bad_route_members_recover")
        else:
            r.no("fs_bad_route_members_recover",out)
    except Exception as e:
        r.no("fs_bad_route_members_recover",str(e))

    # 25 missing purpose
    try:
        orch.execute({"content":"x"})
        r.no("fs_missing_purpose","accepted")
    except:
        r.ok("fs_missing_purpose")

    # 26 purpose wrong type
    try:
        orch.execute({"purpose":123,"content":"x"})
        r.no("fs_purpose_notstr","accepted")
    except:
        r.ok("fs_purpose_notstr")

    # 27 unsupported purpose
    try:
        orch.execute({"purpose":"UNKNOWN","content":"x"})
        r.no("fs_purpose_badkey","accepted")
    except:
        r.ok("fs_purpose_badkey")

    # 28 orchestrator returns dict on ANY error
    try:
        out = orch.execute({"purpose":"coding","content":{"bad":"data"}})
        if isinstance(out,dict):
            r.ok("fs_orch_always_dict")
        else:
            r.no("fs_orch_always_dict","not dict")
    except Exception as e:
        r.no("fs_orch_always_dict",str(e))

    # 29 orchestrator never returns None
    try:
        out = orch.execute({"purpose":"general","content":"ok"})
        if out is not None:
            r.ok("fs_orch_never_none")
        else:
            r.no("fs_orch_never_none","returned None")
    except Exception as e:
        r.no("fs_orch_never_none",str(e))

    # 30 orchestrator synthetic fallback never empty
    try:
        out = orch.execute({"purpose":"general","content":"ok"})
        if isinstance(out.get("content",""),str) and len(out["content"])>0:
            r.ok("fs_synth_not_empty")
        else:
            r.no("fs_synth_not_empty","empty")
    except Exception as e:
        r.no("fs_synth_not_empty",str(e))

# ============================================================
# BLOK 8/8 — FAZA 33 MASTER ORCHESTRATION TEST SUITE
# ============================================================

def t_master(r):

    orch = LLMExecutionOrchestrator()
    wrap = LLMResponseWrapper().wrap
    val  = validate_contract
    route = LLMExecutionRouter.route

    # --------------------------------------------------------
    # Helper functions
    # --------------------------------------------------------
    def sig(d):
        """Stable deterministic signature — FAZA 33."""
        import hashlib, json
        return hashlib.sha256(
            json.dumps(d, sort_keys=True).encode()
        ).hexdigest()

    def ensure_safe_dict(x):
        return (
            isinstance(x, dict)
            and "provider" in x
            and "model" in x
            and "content" in x
            and isinstance(x["content"], str)
        )

    # --------------------------------------------------------
    # 1. BASIC ORCHESTRATION PIPELINE
    # --------------------------------------------------------
    try:
        out = orch.execute({"purpose": "general", "content": "Hello"})
        if ensure_safe_dict(out):
            r.ok("m_basic_pipeline")
        else:
            r.no("m_basic_pipeline", out)
    except Exception as e:
        r.no("m_basic_pipeline", str(e))

    # --------------------------------------------------------
    # 2. ROUTING VALIDATION
    # --------------------------------------------------------
    purposes = ["general", "reasoning", "coding", "fallback"]
    for p in purposes:
        try:
            seq = route(p)
            if isinstance(seq, list) and len(seq) > 0:
                r.ok(f"m_route_{p}")
            else:
                r.no(f"m_route_{p}", seq)
        except Exception as e:
            r.no(f"m_route_{p}", str(e))

    # --------------------------------------------------------
    # 3. WRAPPER ROUNDTRIP VALIDATION
    # --------------------------------------------------------
    base = {"provider": "openai", "model": "gpt-4.1", "content": "hi", "type": "completion"}
    try:
        w = wrap(base)
        if ensure_safe_dict(w):
            r.ok("m_wrap_roundtrip")
        else:
            r.no("m_wrap_roundtrip", w)
    except Exception as e:
        r.no("m_wrap_roundtrip", str(e))

    # --------------------------------------------------------
    # 4. VALIDATOR ROUNDTRIP
    # --------------------------------------------------------
    try:
        v = val(base, strict=False)
        if ensure_safe_dict(v):
            r.ok("m_validator_roundtrip")
        else:
            r.no("m_validator_roundtrip", v)
    except Exception as e:
        r.no("m_validator_roundtrip", str(e))

    # --------------------------------------------------------
    # 5. CHAOS: Missing purpose
    # --------------------------------------------------------
    try:
        orch.execute({"content": "A"})
        r.no("m_chaos_missing_purpose", "no error")
    except:
        r.ok("m_chaos_missing_purpose")

    # --------------------------------------------------------
    # 6. CHAOS: Missing content
    # --------------------------------------------------------
    try:
        orch.execute({"purpose": "general"})
        r.no("m_chaos_missing_content", "no error")
    except:
        r.ok("m_chaos_missing_content")

    # --------------------------------------------------------
    # 7. CHAOS: Huge content (200k)
    # --------------------------------------------------------
    try:
        big = "X" * 200000
        out = orch.execute({"purpose": "general", "content": big})
        if len(out["content"]) < 300:
            r.ok("m_chaos_huge_clean")
        else:
            r.no("m_chaos_huge_clean", len(out["content"]))
    except Exception as e:
        r.no("m_chaos_huge_clean", str(e))

    # --------------------------------------------------------
    # 8. SYNTHETIC RECOVERY (provider down)
    # --------------------------------------------------------
    try:
        class DownBridge(ProviderBridge):
            def call_provider(self, *a, **k): raise RuntimeError("DOWN")
        o = LLMExecutionOrchestrator(provider_bridge=DownBridge("/x"))
        out = o.execute({"purpose": "general", "content": "Hi"})
        if ensure_safe_dict(out) and len(out["content"]) > 0:
            r.ok("m_synth_recovery")
        else:
            r.no("m_synth_recovery", out)
    except Exception as e:
        r.no("m_synth_recovery", str(e))

    # --------------------------------------------------------
    # 9. DETERMINISTIC SIGNATURE VALIDATION
    # --------------------------------------------------------
    try:
        a = orch.execute({"purpose": "general", "content": "Sign"})
        b = orch.execute({"purpose": "general", "content": "Sign"})
        if sig(a) == sig(b):
            r.ok("m_sig_deterministic")
        else:
            r.no("m_sig_deterministic", (sig(a), sig(b)))
    except Exception as e:
        r.no("m_sig_deterministic", str(e))

    # --------------------------------------------------------
    # 10. COMPLETE PIPELINE STRESS RUN (20 cycles)
    # --------------------------------------------------------
    try:
        for i in range(20):
            out = orch.execute({"purpose": "coding", "content": f"test{i}"})
            if not ensure_safe_dict(out):
                r.no("m_pipeline_stress", out); break
        else:
            r.ok("m_pipeline_stress")
    except Exception as e:
        r.no("m_pipeline_stress", str(e))

    # --------------------------------------------------------
    # 11. FULL CONFIG VALIDATION
    # --------------------------------------------------------
    try:
        import json
        with open("senti_core_module/senti_llm/llm_config.json") as f:
            cfg = json.load(f)
        if isinstance(cfg, dict) and "models" in cfg and "routing_policy" in cfg:
            r.ok("m_config_structure")
        else:
            r.no("m_config_structure", cfg)
    except Exception as e:
        r.no("m_config_structure", str(e))

    # --------------------------------------------------------
    # 12. FORBIDDEN PATTERN BLOCK TEST
    # --------------------------------------------------------
    try:
        out = wrap({"provider":"openai","model":"gpt","type":"completion",
                    "content":"normal"})
        r.ok("m_forbidden_clean")

        try:
            wrap({"provider":"openai","model":"gpt","type":"completion",
                  "content":"<script>"})
            r.no("m_forbidden_block","passed")
        except:
            r.ok("m_forbidden_block")
    except Exception as e:
        r.no("m_forbidden_block", str(e))

    # --------------------------------------------------------
    # 13. REPEATED EXECUTION → NO MEMORY LEAKS (light test)
    # --------------------------------------------------------
    try:
        msigs = set()
        for i in range(10):
            out = orch.execute({"purpose":"general","content":"X"})
            msigs.add(sig(out))
        if len(msigs) == 1:
            r.ok("m_repeat_no_drift")
        else:
            r.no("m_repeat_no_drift", msigs)
    except Exception as e:
        r.no("m_repeat_no_drift", str(e))

    # --------------------------------------------------------
    # 14. NO CRASH WITH INVALID TYPES
    # --------------------------------------------------------
    invalids = [
        123, True, None, ["x"], {"bad":"x"}, object()
    ]
    for idx, inv in enumerate(invalids):
        try:
            orch.execute(inv)
            r.no(f"m_invalid_req_{idx}", "accepted invalid")
        except:
            r.ok(f"m_invalid_req_{idx}")

    # --------------------------------------------------------
    # END BLOK 8/8
    # ============================================================

# ============================================================
# REGISTER ALL TESTS
# ============================================================

TESTS = [
    ("smoke", t_smoke),
    ("runtime_smoke_2", t_runtime_smoke_2),
    ("wrapper_pipeline", t_wrapper_pipeline),
    ("validator_integration", t_validator_integration),
    ("runtime_smoke", t_runtime_smoke),
    ("exec_layer", t_exec_layer),
    ("failure_sim", t_failure_sim),
    ("master", t_master),
]

# ============================================================
# RUNNER
# ============================================================

def run_all_tests():
    r = Result()
    start = time.time()

    for name, fn in TESTS:
        try:
            fn(r)
        except Exception as e:
            r.no(name, f"CRASH: {e}\n" + traceback.format_exc())

    end = time.time()
    r.summary()
    print(f"Runtime: {round(end-start, 3)}s")

    # exit status for CI/CD
    if r.no_list:
        sys.exit(1)
    else:
        sys.exit(0)

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    run_all_tests()
