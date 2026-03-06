"""
Generational References — Layer 1 of Enhanced Memory Safety.

Every heap object gets a generation number. Fat pointers store both the
address AND the expected generation. When freed, the generation increments.
Old pointers see the mismatch and trap safely with a plain English message.
"""


class SafetyError(Exception):
    """Raised when a memory safety violation is detected at runtime."""
    pass


class GenRef:
    """A generational reference — a fat pointer carrying addr + gen + metadata."""
    __slots__ = ('addr', 'gen', 'ref_type', 'debug_name', 'alloc_line')

    def __init__(self, addr, gen, ref_type='object', debug_name='unknown', alloc_line=0):
        self.addr = addr
        self.gen = gen
        self.ref_type = ref_type
        self.debug_name = debug_name
        self.alloc_line = alloc_line

    def __repr__(self):
        return f"GenRef(addr={self.addr}, gen={self.gen}, name='{self.debug_name}')"


class HeapSlot:
    """One slot in the generational heap."""
    __slots__ = ('data', 'gen', 'size', 'is_free', 'type_name')

    def __init__(self):
        self.data = None
        self.gen = 0
        self.size = 0
        self.is_free = True
        self.type_name = ''


class GenerationalHeap:
    """
    A simulation of the generational heap used by the Enhanced compiler
    for static analysis and test-time validation.
    """
    DEFAULT_CAPACITY = 1024

    def __init__(self, capacity=None):
        self.capacity = capacity or self.DEFAULT_CAPACITY
        self.slots = [HeapSlot() for _ in range(self.capacity)]
        self.next_free = 0

    def _find_free_slot(self):
        """Find the next available slot, expanding if necessary."""
        start = self.next_free
        for i in range(self.capacity):
            idx = (start + i) % self.capacity
            if self.slots[idx].is_free:
                self.next_free = (idx + 1) % self.capacity
                return idx
        # Expand heap
        old_cap = self.capacity
        self.capacity *= 2
        self.slots.extend(HeapSlot() for _ in range(old_cap))
        self.next_free = old_cap + 1
        return old_cap

    def allocate(self, ref_type, value, debug_name='unknown', alloc_line=0):
        """Allocate a value on the heap and return a GenRef to it."""
        idx = self._find_free_slot()
        slot = self.slots[idx]
        slot.data = value
        slot.gen = slot.gen  # keep current gen (it was incremented on free)
        slot.size = 1
        slot.is_free = False
        slot.type_name = ref_type
        return GenRef(addr=idx, gen=slot.gen, ref_type=ref_type,
                      debug_name=debug_name, alloc_line=alloc_line)

    def free(self, ref, free_line=0):
        """Free the object at the given GenRef. Increments generation."""
        self._validate_ref(ref, free_line)
        slot = self.slots[ref.addr]
        slot.data = None
        slot.gen += 1
        slot.is_free = True

    def deref(self, ref, access_line=0):
        """Dereference a GenRef, returning the stored value. Traps on mismatch."""
        self._validate_ref(ref, access_line)
        return self.slots[ref.addr].data

    def is_valid(self, ref):
        """Check if a GenRef is still valid (gen matches), no side effects."""
        if ref.addr < 0 or ref.addr >= len(self.slots):
            return False
        slot = self.slots[ref.addr]
        return (not slot.is_free) and slot.gen == ref.gen

    def _validate_ref(self, ref, line=0):
        if ref.addr < 0 or ref.addr >= len(self.slots):
            raise SafetyError(
                f"You tried to use '{ref.debug_name}' but it points to invalid memory. "
                f"This should never happen — it may be a compiler bug."
            )
        slot = self.slots[ref.addr]
        if slot.is_free or slot.gen != ref.gen:
            raise SafetyError(
                f"You tried to use '{ref.debug_name}' after it was already freed on line {ref.alloc_line}.\n"
                f"Once you free something, you can't use it anymore."
            )
