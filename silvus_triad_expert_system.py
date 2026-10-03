"""
Silvus Radio + Triad RF BDA Rule-Based Expert System
----------------------------------------------------
Educational / maintenance-support prototype.

Inference method:
    Forward chaining (data-driven)

Important:
    Thresholds such as exact DC voltage, maximum RF input power, temperature
    limits, and model-specific alarm meanings must be verified against the
    exact Silvus radio manual and Triad BDA datasheet for the deployed models.
"""

from dataclasses import dataclass
from typing import Dict, List, Set, Tuple


# ============================================================
# 1. PROPOSITION SYMBOLS
# ============================================================
# Atomic propositions are represented as facts. A proposition is true when
# its symbol exists in the fact set.

PROPOSITIONS: Dict[str, str] = {
    "P1":  "radio_power_ok",
    "P2":  "radio_boot_ok",
    "P3":  "radio_link_up",
    "P4":  "radio_link_unstable",
    "P5":  "radio_link_down",
    "P6":  "radio_high_temperature",
    "P7":  "radio_low_voltage",
    "P8":  "radio_high_voltage",
    "P9":  "radio_tx_enabled",
    "P10": "radio_rx_activity_present",
    "P11": "radio_high_interference",
    "P12": "radio_antenna_connected",
    "P13": "radio_rf_connector_ok",
    "P14": "radio_network_config_ok",
    "P15": "radio_firmware_ok",
    "P16": "radio_ptt_ok",
    "P17": "radio_gps_ok",
    "P18": "radio_ethernet_ok",
    "P19": "bda_power_ok",
    "P20": "bda_rf_input_ok",
    "P21": "bda_rf_output_ok",
    "P22": "bda_antenna_connected",
    "P23": "bda_rf_connectors_ok",
    "P24": "bda_dc_connector_ok",
    "P25": "bda_overtemperature",
    "P26": "bda_low_supply_voltage",
    "P27": "bda_high_supply_voltage",
    "P28": "bda_gain_expected",
    "P29": "bda_alarm_present",
    "P30": "bda_load_or_antenna_mismatch",
    "P31": "bda_input_power_within_limit",
    "P32": "bda_output_path_ok",
    "P33": "system_rf_path_ok",
    "P34": "system_power_path_ok",
}

# Human-readable proposition descriptions.
PROPOSITION_TEXT = {
    k: v.replace("_", " ").capitalize() for k, v in PROPOSITIONS.items()
}


# ============================================================
# 2. RULE MODEL
# ============================================================

@dataclass(frozen=True)
class Rule:
    rule_id: str
    conditions: frozenset[str]
    conclusion: str
    explanation: str


RULES: List[Rule] = [
    Rule(
        "R1",
        frozenset({"radio_power_ok", "radio_boot_ok", "radio_link_down"}),
        "radio_link_fault",
        "Radio powers and boots, but no link is established; investigate RF path, configuration, interference, and peer availability.",
    ),
    Rule(
        "R2",
        frozenset({"radio_power_ok", "radio_boot_ok", "radio_high_interference", "radio_link_unstable"}),
        "radio_interference_fault",
        "The radio is operational but link stability is degraded while interference is present.",
    ),
    Rule(
        "R3",
        frozenset({"radio_low_voltage", "radio_link_unstable"}),
        "radio_power_integrity_fault",
        "Low supply voltage together with an unstable link indicates a power-integrity issue should be investigated.",
    ),
    Rule(
        "R4",
        frozenset({"radio_high_temperature", "radio_link_unstable"}),
        "radio_thermal_fault",
        "High radio temperature together with an unstable link indicates a thermal condition may be affecting operation.",
    ),
    Rule(
        "R5",
        frozenset({"radio_antenna_connected", "radio_rf_connector_ok", "radio_tx_enabled", "radio_rx_activity_present", "radio_link_down"}),
        "radio_configuration_or_peer_fault",
        "The local RF path appears connected and active, yet no link exists; check mission/network configuration and peer compatibility.",
    ),
    Rule(
        "R6",
        frozenset({"radio_network_config_ok", "radio_firmware_ok", "radio_power_ok", "radio_boot_ok", "radio_link_down"}),
        "radio_rf_environment_fault",
        "Power, boot, configuration and firmware are apparently valid, but the link remains down; inspect RF environment, antenna path, interference, and peer node.",
    ),
    Rule(
        "R7",
        frozenset({"bda_power_ok", "bda_rf_input_ok", "bda_rf_output_ok", "bda_antenna_connected", "bda_gain_expected"}),
        "bda_basic_operation_ok",
        "BDA power, RF input, RF output, antenna connection and expected gain are all present.",
    ),
    Rule(
        "R8",
        frozenset({"bda_power_ok", "bda_overtemperature", "bda_rf_output_ok"}),
        "bda_thermal_condition",
        "BDA output is present but the BDA is overtemperature; inspect cooling, mounting, ambient conditions and duty cycle.",
    ),
    Rule(
        "R9",
        frozenset({"bda_low_supply_voltage", "bda_power_ok", "bda_gain_expected"}),
        "bda_supply_fault",
        "The BDA is powered but supply voltage is low; verify the DC source, harness, connector and voltage drop under load.",
    ),
    Rule(
        "R10",
        frozenset({"bda_input_power_within_limit", "bda_antenna_connected", "bda_rf_connectors_ok", "bda_load_or_antenna_mismatch"}),
        "bda_rf_load_mismatch_fault",
        "The RF input and connections appear acceptable, but a load/antenna mismatch is indicated; inspect antenna, cable, connectors and load.",
    ),
    Rule(
        "R11",
        frozenset({"bda_rf_input_ok", "bda_rf_output_ok", "radio_tx_enabled", "radio_link_down"}),
        "integrated_rf_path_fault",
        "Radio TX and BDA RF input/output are present, yet the link is down; investigate antenna path, frequency/band compatibility, interference and system configuration.",
    ),
    Rule(
        "R12",
        frozenset({"radio_power_ok", "radio_boot_ok", "radio_network_config_ok", "radio_rf_connector_ok", "radio_antenna_connected", "bda_power_ok", "bda_rf_input_ok", "bda_rf_output_ok"}),
        "system_operational_path_verified",
        "The principal radio and BDA functional checks are positive; remaining faults should be isolated using link metrics, interference data and component substitution/test equipment.",
    ),
]


# ============================================================
# 3. USER QUESTIONS
# ============================================================

QUESTIONS = [
    ("Q1", "radio_power_ok", "Does the Silvus radio power on normally?"),
    ("Q2", "radio_boot_ok", "Does the radio complete its normal boot sequence?"),
    ("Q3", "radio_link_up", "Is the radio currently establishing a link with the intended peer/node?"),
    ("Q4", "radio_link_unstable", "Is the radio link intermittent or unstable?"),
    ("Q5", "radio_link_down", "Is the radio link completely down?"),
    ("Q6", "radio_high_temperature", "Does the radio report or indicate an abnormally high temperature?"),
    ("Q7", "radio_low_voltage", "Is the radio supply voltage below the approved/model-specific operating range?"),
    ("Q8", "radio_high_interference", "Does the radio diagnostic/spectrum view indicate significant interference?"),
    ("Q9", "radio_antenna_connected", "Is the radio antenna correctly connected?"),
    ("Q10", "radio_rf_connector_ok", "Are the radio RF connectors/cables secure and undamaged?"),
    ("Q11", "radio_network_config_ok", "Are frequency, bandwidth, network/mission profile and other configuration parameters verified?"),
    ("Q12", "radio_firmware_ok", "Is the installed radio firmware known to be approved/compatible for this configuration?"),
    ("Q13", "radio_tx_enabled", "Is radio transmission enabled?"),
    ("Q14", "radio_rx_activity_present", "Is receive activity visible in the radio diagnostics?"),
    ("Q15", "bda_power_ok", "Does the Triad BDA power up normally?"),
    ("Q16", "bda_rf_input_ok", "Is RF input from the radio present and within the approved input range?"),
    ("Q17", "bda_rf_output_ok", "Is RF output from the BDA present?"),
    ("Q18", "bda_antenna_connected", "Is the BDA antenna/load correctly connected to the ANTENNA port?"),
    ("Q19", "bda_rf_connectors_ok", "Are the BDA RF connectors, cables and mating surfaces secure and undamaged?"),
    ("Q20", "bda_dc_connector_ok", "Is the BDA DC/control connector and harness secure, correctly oriented and undamaged?"),
    ("Q21", "bda_overtemperature", "Is the BDA reporting or exhibiting an overtemperature condition?"),
    ("Q22", "bda_low_supply_voltage", "Is BDA supply voltage below its approved/model-specific minimum under load?"),
    ("Q23", "bda_input_power_within_limit", "Has the BDA RF input power been verified to be within the exact datasheet limit?"),
    ("Q24", "bda_gain_expected", "Is the measured BDA gain/output approximately consistent with the expected/model-specific value?"),
    ("Q25", "bda_load_or_antenna_mismatch", "Is there evidence of an antenna/load/cable mismatch?"),
]


# ============================================================
# 4. FORWARD-CHAINING INFERENCE ENGINE
# ============================================================

def forward_chain(initial_facts: Set[str]) -> Tuple[Set[str], List[str], List[str]]:
    """
    Forward chaining:
        facts + rule conditions -> new fact

    Repeats until no rule can add a new fact.
    Returns:
        all derived facts,
        fired rule IDs,
        inference trace.
    """
    facts = set(initial_facts)
    fired_rules: List[str] = []
    trace: List[str] = []

    changed = True
    while changed:
        changed = False

        for rule in RULES:
            if rule.conditions.issubset(facts) and rule.conclusion not in facts:
                facts.add(rule.conclusion)
                fired_rules.append(rule.rule_id)
                trace.append(
                    f"{rule.rule_id}: {format_conditions(rule.conditions)} "
                    f"-> {rule.conclusion}"
                )
                changed = True

    return facts, fired_rules, trace


def format_conditions(conditions: Set[str]) -> str:
    return " AND ".join(sorted(conditions))


def explain_fact(fact: str) -> str:
    for rule in RULES:
        if rule.conclusion == fact:
            return f"{rule.rule_id}: {rule.explanation}"
    return "Initial/user-supplied fact."


# ============================================================
# 5. INTERACTIVE QUESTIONNAIRE
# ============================================================

def ask_user_facts() -> Set[str]:
    print("\n=== Silvus Radio + Triad BDA Troubleshooting Expert System ===")
    print("Answer y/n. Only positive answers are inserted as facts.")
    print("Use the exact equipment manuals/datasheets for limits and safety checks.\n")

    facts: Set[str] = set()

    for qid, symbol, question in QUESTIONS:
        while True:
            answer = input(f"{qid}. {question} [y/n]: ").strip().lower()
            if answer in {"y", "yes", "n", "no"}:
                break
            print("Please enter y or n.")

        if answer in {"y", "yes"}:
            facts.add(symbol)

    return facts


# ============================================================
# 6. DIAGNOSTIC REPORT
# ============================================================

def print_report(initial_facts: Set[str], all_facts: Set[str],
                 fired_rules: List[str], trace: List[str]):

    derived = sorted(all_facts - initial_facts)

    print("\n" + "=" * 70)
    print("INFERENCE REPORT")
    print("=" * 70)

    print("\nInitial facts:")
    for fact in sorted(initial_facts):
        print(f"  + {fact}")

    print("\nDerived facts:")
    if derived:
        for fact in derived:
            print(f"  -> {fact}")
    else:
        print("  No rule fired.")

    print("\nFired rules:")
    if fired_rules:
        for rid in fired_rules:
            print(f"  {rid}")
    else:
        print("  None")

    print("\nInference trace:")
    if trace:
        for i, item in enumerate(trace, 1):
            print(f"  {i}. {item}")
    else:
        print("  No inference was possible.")

    print("\nMaintenance / troubleshooting conclusions:")
    conclusions = [
        f for f in derived
        if f.endswith("_fault")
        or f.endswith("_condition")
        or f.endswith("_ok")
        or f in {"integrated_rf_path_fault", "radio_configuration_or_peer_fault"}
    ]

    if conclusions:
        for fact in conclusions:
            print(f"\n  [{fact}]")
            print(f"    {explain_fact(fact)}")
    else:
        print("  The knowledge base did not reach a specific conclusion.")
        print("  Escalate to detailed manual diagnostics/test equipment.")

    print("\nNOTE:")
    print("This is a rule-based decision-support prototype, not a substitute")
    print("for the applicable equipment manual, datasheet, electrical/RF")
    print("safety procedures, or qualified maintenance personnel.")


# ============================================================
# 7. DEMONSTRATION WITHOUT USER INPUT
# ============================================================

def demo():
    """
    Example:
      radio powers and boots,
      RF path is connected,
      TX is enabled,
      receive activity exists,
      link is down.

    R5 should derive radio_configuration_or_peer_fault.
    """

    demo_facts = {
        "radio_power_ok",
        "radio_boot_ok",
        "radio_link_down",
        "radio_antenna_connected",
        "radio_rf_connector_ok",
        "radio_tx_enabled",
        "radio_rx_activity_present",
    }

    all_facts, fired, trace = forward_chain(demo_facts)
    print_report(demo_facts, all_facts, fired, trace)


if __name__ == "__main__":
    print("1 = Interactive troubleshooting")
    print("2 = Run demonstration")
    choice = input("Select mode [1/2]: ").strip()

    if choice == "2":
        demo()
    else:
        initial = ask_user_facts()
        all_facts, fired, trace = forward_chain(initial)
        print_report(initial, all_facts, fired, trace)
