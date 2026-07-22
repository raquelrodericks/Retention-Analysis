import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

df = pd.read_csv("subscription_data.csv")

# ---- Headline metrics ----
ret_ap = df.loc[df.autopay_week1, "retained_6m"].mean()
ret_mp = df.loc[~df.autopay_week1, "retained_6m"].mean()
overall = df.retained_6m.mean()

# Churn reason split among users who churned, by autopay status
churned = df[~df.retained_6m]
split = (churned.groupby(["autopay_week1", "churn_reason"]).size()
         .groupby(level=0).apply(lambda s: s / s.sum()))

# Of ALL manual-pay churn, how much is involuntary (payment failure)?
mp_churn = churned[~churned.autopay_week1]
inv_share_mp = (mp_churn.churn_reason == "payment_failure").mean()

# Involuntary churn as a share of the entire manual-pay base
mp_base = (~df.autopay_week1).sum()
inv_of_base = (df[(~df.autopay_week1) & (df.churn_reason == "payment_failure")].shape[0]) / mp_base

print(f"6-mo retention | autopay:   {ret_ap:.1%}")
print(f"6-mo retention | manualpay: {ret_mp:.1%}")
print(f"6-mo retention | overall:   {overall:.1%}")
print(f"Retention gap (pp):         {(ret_ap-ret_mp)*100:.1f}")
print(f"Share of manual-pay churn that is payment_failure: {inv_share_mp:.1%}")
print(f"Payment-failure churn as % of manual-pay base:     {inv_of_base:.1%}")

# ---- Monthly retention curve by autopay ----
def survival_curve(sub):
    # fraction still active at end of each month 1..6
    n = len(sub)
    return [ (sub.months_active >= m).mean() for m in range(1,7) ]

curve_ap = survival_curve(df[df.autopay_week1])
curve_mp = survival_curve(df[~df.autopay_week1])

# ---- Chart ----
mpl.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 11,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": 0.25, "grid.linewidth": 0.6,
})
INK="#1a2b3c"; TEAL="#0f8a8a"; CORAL="#e5643e"; MUTE="#8a9199"

fig, ax = plt.subplots(figsize=(8.2, 4.3), dpi=150)
months = list(range(1,7))
ax.plot(months, [c*100 for c in curve_ap], marker="o", color=TEAL, lw=2.4, label="Autopay set up in week 1")
ax.plot(months, [c*100 for c in curve_mp], marker="o", color=CORAL, lw=2.4, label="Manual payment")

for x,y in zip(months,[c*100 for c in curve_ap]):
    if x in (1,6): ax.annotate(f"{y:.0f}%", (x,y), textcoords="offset points", xytext=(0,9), ha="center", color=TEAL, fontweight="bold", fontsize=10)
for x,y in zip(months,[c*100 for c in curve_mp]):
    if x in (1,6): ax.annotate(f"{y:.0f}%", (x,y), textcoords="offset points", xytext=(0,-15), ha="center", color=CORAL, fontweight="bold", fontsize=10)

ax.set_title("Subscription retention by week-1 autopay setup", color=INK, fontweight="bold", pad=12)
ax.set_xlabel("Months since signup"); ax.set_ylabel("% still active")
ax.set_ylim(40,101); ax.set_xlim(0.8,6.2)
ax.legend(frameon=False, loc="lower left")
gap = (curve_ap[-1]-curve_mp[-1])*100
ax.annotate(f"{gap:.0f} pp gap\nat month 6",
            xy=(6, curve_mp[-1]*100), xytext=(4.4, 62),
            color=INK, fontsize=10, fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=MUTE, lw=1.2))
plt.tight_layout()
plt.savefig("retention_chart.png", bbox_inches="tight", facecolor="white")
print("saved retention_chart.png")
