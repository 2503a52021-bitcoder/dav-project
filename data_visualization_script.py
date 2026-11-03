import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def generate_ocean_waste_visualizations(cleaned_file_path: str):
    """
    Generates publication-quality charts for the Ocean Waste project.
    """
    df = pd.read_csv(cleaned_file_path)
    
    # Set aesthetics
    sns.set_theme(style="whitegrid")
    plt.rcParams.update({'font.sans-serif': 'Helvetica', 'font.family': 'sans-serif'})
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    fig.suptitle('Ocean Waste Trend & Management Analysis (1900–2026)', fontsize=18, fontweight='bold', y=0.98)
    
    # Chart 1: Waste Sources vs Ocean Waste Trajectory
    ax1 = axes[0, 0]
    ax1.plot(df['year'], df['plastic_waste_mt'], label='Plastic Waste', color='#e11d48', linewidth=2.5)
    ax1.plot(df['year'], df['fishing_waste_mt'], label='Fishing Waste', color='#f97316', linewidth=2)
    ax1.plot(df['year'], df['other_waste_mt'], label='Other Waste', color='#64748b', linewidth=2)
    ax1.plot(df['year'], df['ocean_waste_mt'], label='Ocean Leakage', color='#0284c7', linewidth=2.5, linestyle='--')
    ax1.set_title('1. Waste Generation by Source vs. Net Ocean Leakage', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Metric Tons (MT)')
    ax1.legend(loc='upper left')
    
    # Chart 2: Management Efficiency vs Actual Ocean Waste Growth
    ax2 = axes[0, 1]
    ax2_twin = ax2.twinx()
    p1 = ax2.plot(df['year'], df['ocean_waste_mt'], color='#0f172a', linewidth=2.5, label='Ocean Waste (MT)')
    p2 = ax2_twin.plot(df['year'], df['management_efficiency_%'], color='#10b981', linewidth=2, linestyle=':', label='Efficiency Index (%)')
    ax2.set_title('2. Management Efficiency Index vs. Ocean Waste Accumulation', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Ocean Waste (MT)')
    ax2_twin.set_ylabel('Management Efficiency (%)')
    lines = p1 + p2
    labels = [l.get_label() for l in lines]
    ax2.legend(lines, labels, loc='upper left')
    
    # Chart 3: Collection vs Recycling Funnel (Recent Decades)
    ax3 = axes[1, 0]
    df_recent = df[df['year'] >= 1980]
    ax3.fill_between(df_recent['year'], df_recent['total_waste_generated_mt'], color='#cbd5e1', alpha=0.4, label='Total Generated')
    ax3.fill_between(df_recent['year'], df_recent['waste_collected_mt'], color='#0284c7', alpha=0.6, label='Collected')
    ax3.fill_between(df_recent['year'], df_recent['waste_recycled_mt'], color='#10b981', alpha=0.8, label='Recycled')
    ax3.set_title('3. Mass Balance Funnel: Generated vs Collected vs Recycled (1980-2026)', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Metric Tons (MT)')
    ax3.legend(loc='upper left')
    
    # Chart 4: Reporting Discrepancy Audit (2015-2026)
    ax4 = axes[1, 1]
    df_audit = df[df['year'] >= 2015]
    colors = ['#e11d48' if val > 0.05 else '#0284c7' for val in df_audit['reporting_gap_mt']]
    ax4.bar(df_audit['year'], df_audit['reporting_gap_mt'], color=colors, width=0.6)
    ax4.set_title('4. Data Anomaly Audit: Ocean Waste Reporting Gap (2015–2026)', fontsize=12, fontweight='bold')
    ax4.set_ylabel('Gap (Reported - Expected MT)')
    ax4.axhline(0, color='black', linewidth=0.8)
    
    plt.tight_layout()
    plt.savefig('ocean_waste_visualizations.png', dpi=300)
    print("Visualizations created and saved to 'ocean_waste_visualizations.png'.")
    plt.show()

if __name__ == "__main__":
    # generate_ocean_waste_visualizations('cleaned_ocean_waste_data.csv')
    pass