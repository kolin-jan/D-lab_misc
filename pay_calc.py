import numpy as np

def count_bills(N):
    """
    Break down amount N into bills of different denominations.
    Returns the count of each bill type.
    """
    bills = {
        500: 0,
        200: 0,
        100: 0,
        50: 0,
        20: 0,
        10: 0
    }
    
    remaining = N
    
    bills[500] = remaining // 500
    remaining = remaining % 500
    
    bills[200] = remaining // 200
    remaining = remaining % 200
    
    bills[100] = remaining // 100
    remaining = remaining % 100
    
    bills[50] = remaining // 50
    remaining = remaining % 50
    
    bills[20] = remaining // 20
    remaining = remaining % 20
    
    bills[10] = remaining // 10
    remaining = remaining % 10
    
    return bills, remaining
# simulation setup
simulation_results = {
    500: [],
    200: [],
    100: [],
    50: [],
    20: [],
    10: []
}

total_payments_per_simulation = []

num_simulations = 1000

for sim in range(num_simulations):
    # initialize
    total_bills = {
        500: 0,
        200: 0,
        100: 0,
        50: 0,
        20: 0,
        10: 0
    }
    
    total_payment_this_sim = 0
    
    n = 400  # number of payments
    for iteration in range(n):
        set_reward = 280
        attention_check_reward = 20
        attention_check_prob = 0.8
        attention_check_result = np.random.binomial(n=1, p=attention_check_prob)
        
        willingness_to_work = np.random.uniform(low=0, high=100)
        rnd_work_return = np.random.uniform(low=0, high=100)
        
        if willingness_to_work <= rnd_work_return:
            decleared_work_reward = rnd_work_return
        else:
            decleared_work_reward = 0
        
        treated_work_chance = 0.25
        treated = np.random.binomial(n=1, p=treated_work_chance)
        treated_work_reward_per_minute = 3
        treated_work_time = 30
        treated_work_reward = treated_work_reward_per_minute * treated_work_time * treated
        # total reward calculation
        total_reward = set_reward + attention_check_reward * attention_check_result + decleared_work_reward + treated_work_reward
        # round to nearest 10
        total_reward_rounded = round(total_reward / 10) * 10
        # accumulate total payment for this simulation
        total_payment_this_sim += total_reward_rounded
        # count bills needed
        bills_needed, leftover = count_bills(total_reward_rounded)
        
        for denomination, count in bills_needed.items():
            total_bills[denomination] += count
    
    for denomination in simulation_results.keys():
        simulation_results[denomination].append(total_bills[denomination])
    # accumulate total payment for this simulation
    total_payments_per_simulation.append(total_payment_this_sim)
# print results
print(f"Monte Carlo Simulation Results ({num_simulations} simulations of {n} payments each)")
print("=" * 70)
print(f"\nTotal Payment Statistics:")
mean_total = np.mean(total_payments_per_simulation)
std_total = np.std(total_payments_per_simulation)
min_total = np.min(total_payments_per_simulation)
max_total = np.max(total_payments_per_simulation)

print(f"Expected total payment: {mean_total:.2f} CZK ± {std_total:.2f}")
print(f"Min total payment: {min_total:.2f} CZK")
print(f"Max total payment: {max_total:.2f} CZK")
print(f"95% CI: [{mean_total - 2*std_total:.2f}, {mean_total + 2*std_total:.2f}] CZK")

print(f"\nExpected bills needed (mean ± std):")
for denomination in [500, 200, 100, 50, 20, 10]:
    mean_bills = np.mean(simulation_results[denomination])
    std_bills = np.std(simulation_results[denomination])
    min_bills = np.min(simulation_results[denomination])
    max_bills = np.max(simulation_results[denomination])
    
    print(f"{denomination} CZK: {mean_bills:.1f} ± {std_bills:.1f} bills (min: {min_bills}, max: {max_bills})")

print(f"\n95% confidence intervals for bills (approximately mean ± 2*std):")
for denomination in [500, 200, 100, 50, 20, 10]:
    mean_bills = np.mean(simulation_results[denomination])
    std_bills = np.std(simulation_results[denomination])
    lower = mean_bills - 2 * std_bills
    upper = mean_bills + 2 * std_bills
    
    print(f"{denomination} CZK: [{lower:.0f}, {upper:.0f}] bills")