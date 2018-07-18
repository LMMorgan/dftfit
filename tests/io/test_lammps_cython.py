import asyncio

import pytest

from dftfit.io.lammps_cython import LammpsCythonDFTFITCalculator


@pytest.mark.parametrize('structure_filename, supercell, num_atoms, potential_filename', [
    ('Ne.cif', (2, 2, 2), 32, 'Ne-lennard-jones.yaml'),             # lennard-jones
    ('He.cif', (3, 3, 3), 54, 'He-beck.yaml'),                      # beck
    ('MgO.cif', (2, 2, 2), 64, 'MgO-charge-buck-fitting.yaml'),     # buckingham
    ('MgO.cif', (2, 2, 2), 64, 'MgO-charge-buck-zbl.yaml'),         # zbl
    ('MgO.cif', (2, 2, 2), 64, 'MgO-charge-func.yaml'),             # python-function
    ('LiTaO3.cif', (1, 1, 1), 30, 'LiTaO3-tersoff-2.yaml'),         # tersoff-2
    ('LiTaO3.cif', (1, 1, 1), 30, 'LiTaO3-tersoff-2-charge.yaml'),  # tersoff-2 + charge
    ('3C-SiC.cif', (2, 2, 2), 64, 'SiC-gao-weber.yaml'),            # gao-weber
    ('3C-SiC.cif', (2, 2, 2), 64, 'SiC-tersoff.yaml'),              # tersoff
    ('3C-SiC.cif', (2, 2, 2), 64, 'SiC-vashishta.yaml'),            # vashishta
    ('CdTe.cif', (2, 2, 2), 64, 'CdTe-stillinger-weber.yaml'),      # stillinger-weber
    ('SiO2.cif', (2, 2, 2), 96, 'SiO2-comb.yaml'),                  # comb
    # ('Ti4Cu2O.cif', (1, 1, 1), 112, 'Ti4Cu2O-comb-3.yaml')        # comb-3 (comb-3 freezes...)
])
@pytest.mark.benchmark(group='apply-potential', min_rounds=10)
def test_potential_lammps_cython(
        benchmark, structure, potential,
        structure_filename, supercell, num_atoms, potential_filename):
    s = structure('test_files/structure/%s' % structure_filename) * supercell
    assert len(s) == num_atoms
    p = potential('test_files/potential/%s' % potential_filename)

    calculator = LammpsCythonDFTFITCalculator([s])
    loop = asyncio.get_event_loop()
    loop.run_until_complete(calculator.create())

    # using calculator internals
    lmp = calculator.lammps_systems[-1]

    @benchmark
    def f():
        calculator._apply_potential_files(p)
        calculator._apply_potential(lmp, p)