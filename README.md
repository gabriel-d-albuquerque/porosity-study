# What is it about?
The codes in this repository are part of a project patronized by the University of São Paulo (USP) and developed by the undergraduate student in Aeronautical Engineering Gabriel Delgado Albuquerque, alongside the aid and supervision of Dr. Prof. Ricardo Afonso Angélico, of the Aeronautical Engineering Department of the University of São Paulo.

The core objective of the research is to develop a computational routine able to obtain the effective macroscopic properties of refractory materials. This will be done through the generation of artificial microstructures using a routine developed in Python and the softwares Neper and GMash. Afterwards, the models shall be loaded in the finite elements software Abaqus for the application of the periodic boundary conditions and model analysis.

# How to use it?

## Porosity study
At the current stage of development, the routines have not achieved their final goal. The author of the project is at a preliminary stage, in which tests are being made and key concepts of the field, necessary to the end goal achievement, are being understood.

With that said, to run the codes you will need only to have Abaqus installed in your system and knowledge of how to execute Abaqus scripting files through the Abaqus Command environment. There are also two `.bat` files, for Windows users, which can run the Abaqus scripting files for the user. At the end of the computing process, a report file will be generated stating the stress-strain state, which can be later used by the nonlinear least-squares routine in order to obtain the effective macroscopic properties. The programs also output Abaqus Project files, allowing the user to access all models within the Abaqus visual interface.

The cases covered by the scripts are, at the moment, single RVEs with a circular porus of a specific radius `R`, whose value is calculated by the code through the user input `P`, which stands for the porosity value desired for that RVE. It is possible to assign a list of values to the variable `P`, meaning that several porosity cases can be studied at a time. A single Abaqus Project file is generated, containing separated models respective to each assigned porosity.

## Mesh study
A separate routine is being developed aiming to analyze the influence of the mesh refinement on the convergence of the obtained results. Therefore, the most critical porosity case (70%) has been adopted for this study. The same geometric model is being subjected to analysis with a varying mesh size and two stress components are being observed. These stress components are relative to the node in the middle of the upper edge of the RVE. The mesh size has a direct impact on the number of elements present in this region and, due to the high porosity, there could be not enough elements for a convergent result to be achieved.

# Next steps
There is still a long path to be covered, but the subsequent work is to develop another routine, able to create several random circular porus within the domain and the usage of this code to generate the microstructure inside Abaqus, along with the periodic boundary conditions.
