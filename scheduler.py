import numpy as np
from typing import List, Dict, Tuple

class RA:
    def __init__(self, name, availability=None, max_slots_per_week=None):
        self.name = name
        # 5 days x 6 time slots matrix
        # 1 = available, 0 = not available
        if availability is None:
            # Default: all available
            self.availability = np.ones((5, 6), dtype=int)
        else:
            self.availability = np.array(availability, dtype=int)
        
        # HARD CONSTRAINT: No sessions on Thursday slots 2 and 3
        self.availability[3, 2] = 0  # Thursday slot 2 (12:45-14:15)
        self.availability[3, 3] = 0  # Thursday slot 3 (14:30-16:00)
        
        # Max slots per week
        if max_slots_per_week is not None:
            self.max_slots_per_week = max_slots_per_week
        else:
            # Default: sum of all available slots in the matrix
            self.max_slots_per_week = int(np.sum(self.availability))
    
    def __repr__(self):
        return f"RA({self.name})"


# Example usage:
# ras = [
#     RA("Alice", 
#        max_slots_per_week=4,
#        availability=[
#         [0, 1, 1, 1, 0, 0],  # Monday: slots 1,2,3
#         [0, 0, 0, 0, 1, 1],  # Tuesday: slots 4,5
#         [0, 0, 0, 0, 1, 1],  # Wednesday: slots 4,5
#         [0, 0, 0, 0, 1, 1],  # Thursday: slots 4,5
#         [1, 1, 1, 1, 0, 0],  # Friday: slots 0,1,2,3
#     ]),
#     RA("Bob",
#        availability=[
#         [1, 1, 1, 1, 1, 1],  # Monday: all slots
#         [0, 1, 1, 0, 0, 0],  # Tuesday: slots 1,2
#         [1, 0, 1, 1, 1, 1],  # Wednesday: slots 0,2,3,4,5
#         [0, 0, 0, 0, 1, 1],  # Thursday: slots 4,5
#         [1, 1, 0, 1, 1, 1],  # Friday: slots 0,1,3,4,5
#     ]),
#     RA("Carol",
#        max_slots_per_week=3,
#        availability=[
#         [0, 0, 0, 0, 0, 0],  # Monday: unavailable
#         [1, 1, 1, 1, 1, 1],  # Tuesday: all slots
#         [1, 1, 1, 1, 1, 1],  # Wednesday: all slots
#         [1, 1, 1, 1, 1, 1],  # Thursday: all slots
#         [0, 0, 0, 0, 0, 0],  # Friday: unavailable
#     ])
# ]


class GreedyScheduler:
    """
    Greedy scheduler using most-constrained-first heuristic
    """
    
    def __init__(self, ras: List[RA]):
        self.ras = ras
        self.schedule = {}  # key: (day, slot), value: [RA names]
        self.ra_stats = {}  # Track assignments per RA
        
        # Initialize tracking
        for ra in ras:
            self.ra_stats[ra.name] = {
                'weekly': 0,
                'daily': [0, 0, 0, 0, 0],  # slots per day
                'slots': []  # list of (day, slot) tuples
            }
    
    def can_assign(self, ra: RA, day: int, slot: int) -> bool:
        """Check if RA can be assigned to this slot (all hard constraints)"""
        # Constraint 1: Availability
        if ra.availability[day, slot] != 1:
            return False
        
        # Constraint 2: Weekly limit
        if self.ra_stats[ra.name]['weekly'] >= ra.max_slots_per_week:
            return False
        
        # Constraint 3: Daily limit (max 2 sessions per day)
        if self.ra_stats[ra.name]['daily'][day] >= 2:
            return False
        
        return True
    
    def assign(self, ra: RA, day: int, slot: int):
        """Assign RA to a slot and update all tracking"""
        key = (day, slot)
        if key not in self.schedule:
            self.schedule[key] = []
        
        self.schedule[key].append(ra.name)
        self.ra_stats[ra.name]['weekly'] += 1
        self.ra_stats[ra.name]['daily'][day] += 1
        self.ra_stats[ra.name]['slots'].append((day, slot))
    
    def get_available_ras(self, day: int, slot: int) -> List[RA]:
        """Get all RAs who can work this slot"""
        return [ra for ra in self.ras if self.can_assign(ra, day, slot)]
    
    def schedule_greedy(self):
        """
        Main greedy scheduling algorithm
        
        Strategy:
        1. Prioritize slots that have RAs with least overall availability
        2. This ensures we use constrained RAs before they run out of capacity
        """
        # Step 1: Build list of all potential slots with their criticality
        slots = []
        
        for day in range(5):
            for slot in range(6):
                available = self.get_available_ras(day, slot)
                
                if len(available) >= 2:
                    # Criticality = prioritize slots with most constrained RAs
                    # Sum of (1 / max_slots_per_week) for available RAs
                    # Higher sum = more constrained RAs available = higher priority
                    criticality = sum(1.0 / ra.max_slots_per_week for ra in available)
                    
                    slots.append((day, slot, criticality))
        
        # Step 2: Sort by criticality (most constrained RAs first)
        slots.sort(key=lambda x: x[2], reverse=True)
        
        # Step 3: Assignment loop
        for day, slot, _ in slots:
            available = self.get_available_ras(day, slot)
            
            if len(available) >= 2:
                # Assign the first 2 available RAs
                self.assign(available[0], day, slot)
                self.assign(available[1], day, slot)
    
    def print_schedule(self):
        """Print the final schedule"""
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
        time_slots = ['9:15-10:45', '11:00-12:30', '12:45-14:15', 
                      '14:30-16:00', '16:15-17:45', '18:00-19:30']
        
        print("\n" + "="*60)
        print("SCHEDULED LAB SESSIONS")
        print("="*60 + "\n")
        
        total_sessions = 0
        
        for day in range(5):
            day_has_sessions = False
            day_output = []
            
            for slot in range(6):
                key = (day, slot)
                if key in self.schedule and len(self.schedule[key]) >= 2:
                    ras = ', '.join(self.schedule[key])
                    day_output.append(f"  {time_slots[slot]}: {ras}")
                    total_sessions += 1
                    day_has_sessions = True
            
            if day_has_sessions:
                print(f"{days[day]}:")
                for line in day_output:
                    print(line)
                print()
        
        print(f"Total sessions covered: {total_sessions} / 28\n")
    
    def print_workload(self):
        """Print workload distribution"""
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
        
        print("="*60)
        print("RA WORKLOAD")
        print("="*60 + "\n")
        
        for ra in self.ras:
            stats = self.ra_stats[ra.name]
            print(f"{ra.name}: {stats['weekly']} slots (limit: {ra.max_slots_per_week})")
            daily_str = ', '.join([f"{days[i]}:{stats['daily'][i]}" for i in range(5)])
            print(f"  Daily breakdown: {daily_str}")
            print()
    
    def calculate_gaps(self) -> Dict[str, int]:
        """Calculate gap slots for each RA"""
        print("="*60)
        print("GAP ANALYSIS (empty slots between assignments)")
        print("="*60 + "\n")
        
        gaps = {}
        
        for ra in self.ras:
            stats = self.ra_stats[ra.name]
            if len(stats['slots']) == 0:
                continue
            
            # Sort slots by day, then by time
            sorted_slots = sorted(stats['slots'], key=lambda x: (x[0], x[1]))
            
            gap_count = 0
            for i in range(1, len(sorted_slots)):
                # Only count gaps on the same day
                if sorted_slots[i][0] == sorted_slots[i-1][0]:
                    gap_size = sorted_slots[i][1] - sorted_slots[i-1][1] - 1
                    if gap_size > 0:
                        gap_count += gap_size
            
            gaps[ra.name] = gap_count
            print(f"{ra.name}: {gap_count} gap slots")
        
        print()
        return gaps
    
    def get_statistics(self):
        """Print overall statistics"""
        print("="*60)
        print("STATISTICS")
        print("="*60 + "\n")
        
        covered = len(self.schedule)
        total_slots = 28  # Updated: 30 - 2 (Thursday slots 2 and 3)
        
        # Count impossible slots (< 2 RAs available)
        impossible = 0
        for day in range(5):
            for slot in range(6):
                # Skip Thursday slots 2 and 3 (already excluded)
                if day == 3 and slot in [2, 3]:
                    continue
                    
                available_count = sum(1 for ra in self.ras if ra.availability[day, slot] == 1)
                if available_count < 2:
                    impossible += 1
        
        theoretical_max = total_slots - impossible
        efficiency = (covered / theoretical_max * 100) if theoretical_max > 0 else 0
        
        print(f"Sessions covered: {covered}")
        print(f"Total slots: {total_slots}")
        print(f"Impossible to cover (<2 RAs available): {impossible}")
        print(f"Theoretical maximum: {theoretical_max}")
        print(f"Efficiency: {efficiency:.1f}%")
        print()