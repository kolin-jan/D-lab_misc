# Research Assistant (RA) Scheduling Optimization Script
# Purpose: Efficiently schedule lab sessions with complex constraints

import numpy as np
from typing import List, Dict, Tuple

class RA:
    """
    Research Assistant class to manage individual availability and constraints
    
    Key Features:
    - Customizable availability matrix
    - Configurable weekly slot limits
    - Built-in time slot restrictions
    """
    def __init__(self, name, availability=None, max_slots_per_week=None):
        # Initialize RA with name, availability, and slot constraints
        self.name = name
        
        # Availability matrix: 5 days x 6 time slots
        # 1 = available, 0 = not available
        if availability is None:
            # Default: all slots initially available
            # Allows full flexibility if no specific constraints provided
            self.availability = np.ones((5, 6), dtype=int)
        else:
            # Use provided availability matrix
            self.availability = np.array(availability, dtype=int)
        
        # HARD CONSTRAINT: No sessions on specific Thursday slots
        # Ensures these slots are always unavailable
        self.availability[3, 2] = 0  # Thursday slot 2 (12:45-14:15)
        self.availability[3, 3] = 0  # Thursday slot 3 (14:30-16:00)
        
        # Set maximum weekly slots
        if max_slots_per_week is not None:
            # Use user-provided limit
            self.max_slots_per_week = max_slots_per_week
        else:
            # Default: sum of all available slots in the matrix
            # Automatically calculates max based on availability
            self.max_slots_per_week = int(np.sum(self.availability))
    
    def __repr__(self):
        # String representation of RA for easy debugging
        return f"RA({self.name})"


class GreedyScheduler:
    """
    Greedy scheduling algorithm with multiple constraint management
    
    Core Scheduling Strategy:
    1. Prioritize slots with most constrained RAs
    2. Ensure all hard constraints are met
    3. Maximize overall schedule coverage
    """
    
    def __init__(self, ras: List[RA]):
        # Initialize scheduler with list of RAs
        self.ras = ras
        self.schedule = {}  # Tracks assigned slots
        self.ra_stats = {}  # Tracks individual RA assignments
        
        # Initialize tracking for each RA
        for ra in ras:
            self.ra_stats[ra.name] = {
                'weekly': 0,  # Total slots assigned this week
                'daily': [0, 0, 0, 0, 0],  # Slots per day
                'slots': []  # List of assigned (day, slot) tuples
            }
    
    def can_assign(self, ra: RA, day: int, slot: int) -> bool:
        """
        Comprehensive constraint checking for RA assignment
        
        Checks:
        1. RA availability for specific slot
        2. Weekly slot limit not exceeded
        3. Daily session limit (max 2 per day)
        """
        # Constraint 1: Check slot availability
        if ra.availability[day, slot] != 1:
            return False
        
        # Constraint 2: Weekly slot limit
        if self.ra_stats[ra.name]['weekly'] >= ra.max_slots_per_week:
            return False
        
        # Constraint 3: Daily session limit (max 2 per day)
        if self.ra_stats[ra.name]['daily'][day] >= 2:
            return False
        
        return True
    
    def assign(self, ra: RA, day: int, slot: int):
        """
        Assign RA to a specific slot and update tracking
        
        Updates:
        - Schedule
        - Weekly slot count
        - Daily slot count
        - RA's assigned slots
        """
        key = (day, slot)
        if key not in self.schedule:
            self.schedule[key] = []
        
        # Add RA to slot
        self.schedule[key].append(ra.name)
        
        # Update tracking
        self.ra_stats[ra.name]['weekly'] += 1
        self.ra_stats[ra.name]['daily'][day] += 1
        self.ra_stats[ra.name]['slots'].append((day, slot))
    
    def get_available_ras(self, day: int, slot: int) -> List[RA]:
        """
        Find all RAs available for a specific slot
        
        Filters RAs based on all constraint checks
        """
        return [ra for ra in self.ras if self.can_assign(ra, day, slot)]
    
    def schedule_greedy(self):
        """
        Main scheduling algorithm
        
        Key Steps:
        1. Identify potential slots
        2. Calculate slot criticality
        3. Prioritize most constrained slots
        4. Assign RAs systematically
        """
        # Identify potential slots
        slots = []
        
        for day in range(5):
            for slot in range(6):
                available = self.get_available_ras(day, slot)
                
                # Require at least 2 RAs available
                if len(available) >= 2:
                    # Calculate criticality based on RA constraints
                    # Higher criticality = more constrained RAs
                    criticality = sum(1.0 / ra.max_slots_per_week for ra in available)
                    
                    slots.append((day, slot, criticality))
        
        # Sort slots by criticality (most constrained first)
        slots.sort(key=lambda x: x[2], reverse=True)
        
        # Assign RAs to slots
        for day, slot, _ in slots:
            available = self.get_available_ras(day, slot)
            
            # Ensure at least 2 RAs can be assigned
            if len(available) >= 2:
                self.assign(available[0], day, slot)
                self.assign(available[1], day, slot)
    
    # Additional methods for reporting and analysis 
    # (print_schedule, print_workload, calculate_gaps, get_statistics)
    # Omitted for brevity, but provide comprehensive scheduling insights

# Example Usage:
def main():
    """
    Demonstration of how to use the RA scheduling system
    
    Shows how to:
    1. Create RAs with different constraints
    2. Initialize scheduler
    3. Generate schedule
    4. Analyze results
    """
    ras = [
        RA("Alice", 
           max_slots_per_week=4,
           availability=[
               [0, 1, 1, 1, 0, 0],  # Varied availability
               [0, 0, 0, 0, 1, 1],
               [0, 0, 0, 0, 1, 1],
               [0, 0, 0, 0, 1, 1],
               [1, 1, 1, 1, 0, 0],
           ]),
        RA("Bob",
           availability=[
               [1, 1, 1, 1, 1, 1],  # More flexible
               [0, 1, 1, 0, 0, 0],
               [1, 0, 1, 1, 1, 1],
               [0, 0, 0, 0, 1, 1],
               [1, 1, 0, 1, 1, 1],
           ])
    ]

    # Create and run scheduler
    scheduler = GreedyScheduler(ras)
    scheduler.schedule_greedy()
    
    # Generate reports
    scheduler.print_schedule()
    scheduler.print_workload()
    scheduler.get_statistics()

if __name__ == "__main__":
    main()

# Key Design Principles:
# 1. Flexibility in RA availability
# 2. Multiple hard constraints
# 3. Intelligent assignment strategy
# 4. Comprehensive reporting