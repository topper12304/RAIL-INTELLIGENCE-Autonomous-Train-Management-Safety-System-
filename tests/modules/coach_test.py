from .core import CoachDLL


def test_faulty_coach():
    dll = CoachDLL()
    dll.append("C1")
    dll.append("C2", faulty=True)
    dll.append("C3")
    assert dll.find_faulty_index() == 1
