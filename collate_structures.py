import glob
from pymatgen.io.vasp import Poscar
from vasp_outcar import forces_from_outcar, stresses_from_outcar
from lammps_data import LammpsData

def collate_structural_data(params, supercell=None):
    """
    Collects the information needed for the lammps data inputs from the POSCARs and OUTCARs with additional information provided by params.
    
    Args:
        params (dict(dict)): Contains core_shell (bool), charges (float), masses (float), and cs_springs (list(float)) dictionaries where the keys are atom label (str). Also contains bpp (list(float)) and sd (list(float)) dictionaries where the keys are atom label pairs (str), example: 'Li-O'.
        supercell (list(int)): 3 integers defining the cell increase in x, y, and z. Default=None if called directly.
        
    Returns:
        lammps_data (list(obj)):  LammpsData objects containing atom_types (list(obj:AtomType)), bond_types (list(obj:BonType)), atoms (list(obj:Atom)), bonds (list(obj:Bond)), cell_lengths (list(float)), tilt_factor (list(float)), file_name (str), and expected_stress_tensors (np.array).
        """
    if (isinstance(supercell, list) is False) and (supercell is not None):
            raise TypeError('Incorrect type for supercell. Requires integers for x,y,z expansion in a list, e.g. [1,1,1], or list of x,y,z expansions for each structure, e.g. [[1,1,1], [2,2,2], [3,3,3]]. Alternatively do not include.')
            
    lammps_data = []
    for i, pos in enumerate(sorted(glob.glob('poscars/POSCAR*'))):
        structure = Poscar.from_file(pos).structure
        forces = forces_from_outcar('outcars/OUTCAR{}'.format(i+1))[-1]
        stresses = stresses_from_outcar('outcars/OUTCAR{}'.format(i+1))
        structure.add_site_property('forces', forces)
        if supercell is not None:
            if isinstance(supercell[0], int) and len(supercell) == 3:
                structure = structure*supercell
            elif isinstance(supercell[i], list) and (all([len(supercell[i]) == 3 for i, x in enumerate(supercell)])):
                structure = structure*supercell[i]
            else:
                raise ValueError('Incorrect dimensions for supercell. Requires x,y,z expansion (i.e. list of 3 integers) or list of x,y,z expansions for each structure (i.e. list of list(x,y,z))')
 
        struct_data = LammpsData.from_structure(structure, params, i, stresses)
        lammps_data.append(struct_data)  
    return lammps_data