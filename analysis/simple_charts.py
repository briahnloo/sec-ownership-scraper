#!/usr/bin/env python3
"""
Simple matplotlib visualization of institutional market dominance findings.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def create_simple_visualizations():
    """Create simple, clear visualizations of our findings"""
    
    print("📊 Creating simple visualizations of market dominance...")
    
    # Load the comprehensive data
    df = pd.read_csv("../results/comprehensive_market_ownership_20250918_195445.csv")
    
    # Calculate key metrics
    total_companies = df['ticker'].nunique()
    holder_counts = df['holder_name'].value_counts()
    
    print(f"✅ Loaded data: {len(df)} records, {total_companies} companies")
    
    # Create 2x2 subplot layout
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Institutional Market Dominance Analysis\n438 Major American Companies', 
                 fontsize=16, fontweight='bold')
    
    # 1. Market Presence by Institution (Bar Chart)
    percentages = (holder_counts / total_companies * 100)
    top8 = percentages.head(8)
    
    colors = ['#FF4444', '#4444FF', '#44AA44', '#FFAA44', '#AA44FF', '#44AAFF', '#AAAA44', '#FF44AA']
    bars1 = ax1.bar(range(len(top8)), top8.values, color=colors)
    
    ax1.set_xticks(range(len(top8)))
    ax1.set_xticklabels([name.split()[0] for name in top8.index], rotation=45, ha='right')
    ax1.set_ylabel('Market Presence (%)')
    ax1.set_title('Institutional Market Presence')
    ax1.grid(axis='y', alpha=0.3)
    
    # Add percentage labels on bars
    for bar, pct in zip(bars1, top8.values):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f'{pct:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    # 2. Big 2 Dominance (Pie Chart)
    vanguard_companies = set(df[df['holder_name'] == 'Vanguard Group']['ticker'])
    blackrock_companies = set(df[df['holder_name'] == 'BlackRock']['ticker'])
    
    both_companies = len(vanguard_companies & blackrock_companies)
    vanguard_only = len(vanguard_companies - blackrock_companies)
    blackrock_only = len(blackrock_companies - vanguard_companies)
    neither = total_companies - len(vanguard_companies | blackrock_companies)
    
    sizes = [both_companies, vanguard_only, blackrock_only, neither]
    labels = [f'Both V&B\n{both_companies} cos', f'Vanguard Only\n{vanguard_only} cos',
              f'BlackRock Only\n{blackrock_only} cos', f'Neither\n{neither} cos']
    colors2 = ['#FF4444', '#4444FF', '#44AA44', '#CCCCCC']
    
    ax2.pie(sizes, labels=labels, colors=colors2, autopct='%1.1f%%', startangle=90)
    ax2.set_title('Big 2 Market Control\n(Vanguard + BlackRock)')
    
    # 3. Share Holdings (Horizontal Bar Chart)
    shares_by_holder = df.groupby('holder_name')['shares'].sum().sort_values(ascending=False)
    valid_shares = shares_by_holder[shares_by_holder > 0].head(6)
    shares_billions = valid_shares / 1_000_000_000
    
    y_pos = np.arange(len(shares_billions))
    bars3 = ax3.barh(y_pos, shares_billions.values, color=['#FF4444', '#4444FF', '#44AA44', '#FFAA44', '#AA44FF', '#44AAFF'])
    
    ax3.set_yticks(y_pos)
    ax3.set_yticklabels([name.split()[0] for name in shares_billions.index])
    ax3.set_xlabel('Total Shares Held (Billions)')
    ax3.set_title('Share Holdings by Institution')
    ax3.grid(axis='x', alpha=0.3)
    
    # Add value labels
    for i, (bar, value) in enumerate(zip(bars3, shares_billions.values)):
        ax3.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                f'{value:.1f}B', va='center', fontweight='bold')
    
    # 4. Market Concentration Metrics
    # Show cumulative concentration
    institutions = ['BlackRock', 'Vanguard', 'State Street', 'T. Rowe Price', 'Fidelity']
    cumulative_presence = []
    running_companies = set()
    
    for inst in institutions:
        if inst in holder_counts.index:
            inst_companies = set(df[df['holder_name'].str.contains(inst, case=False)]['ticker'])
            running_companies.update(inst_companies)
            cumulative_pct = len(running_companies) / total_companies * 100
            cumulative_presence.append(cumulative_pct)
        else:
            cumulative_presence.append(cumulative_presence[-1] if cumulative_presence else 0)
    
    ax4.plot(range(1, len(cumulative_presence) + 1), cumulative_presence, 
             marker='o', linewidth=3, markersize=8, color='#FF4444')
    ax4.fill_between(range(1, len(cumulative_presence) + 1), cumulative_presence, alpha=0.3, color='#FF4444')
    
    ax4.set_xlabel('Number of Top Institutions')
    ax4.set_ylabel('Cumulative Market Coverage (%)')
    ax4.set_title('Cumulative Market Concentration')
    ax4.grid(True, alpha=0.3)
    ax4.set_ylim(0, 105)
    
    # Add key annotation
    if len(cumulative_presence) >= 2:
        ax4.annotate(f'Top 2: {cumulative_presence[1]:.1f}%', 
                    xy=(2, cumulative_presence[1]), xytext=(3, cumulative_presence[1] - 10),
                    arrowprops=dict(arrowstyle='->', color='red'),
                    fontweight='bold', bbox=dict(boxstyle="round,pad=0.3", facecolor='yellow'))
    
    plt.tight_layout()
    
    # Save the visualization
    filename = "simple_market_dominance_charts.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"💾 Charts saved to: {filename}")
    
    # Show key statistics
    print(f"\n📊 KEY STATISTICS:")
    print(f"   BlackRock presence: {holder_counts.get('BlackRock', 0)} companies ({holder_counts.get('BlackRock', 0)/total_companies*100:.1f}%)")
    print(f"   Vanguard presence: {holder_counts.get('Vanguard Group', 0)} companies ({holder_counts.get('Vanguard Group', 0)/total_companies*100:.1f}%)")
    print(f"   Combined Big 2: {len(vanguard_companies | blackrock_companies)} companies ({len(vanguard_companies | blackrock_companies)/total_companies*100:.1f}%)")
    
    plt.show()
    
    return df

if __name__ == "__main__":
    df = create_simple_visualizations()
    print(f"\n🎉 Simple visualization complete!")
    print(f"📈 The charts clearly show unprecedented institutional market dominance")
