# each dict entry corresponds to a cpp-class 
# each class has a ordered list of needed sub-classes
# possible outer structures (runnables) are marked with '!'
# lists of the form [ "Mesh::" ] get auto expanded to [ "Mesh::StructuredRegularFixedOfDimension", "Mesh::Str..", ... ]
possible_solver_combinations = {
    "!SpatialDiscretization::FiniteElementMethod" : [
        [ "Mesh::" ],
        [ "BasisFunction::" ],
        [ "Quadrature::" ],
        [ "Equation::" ]
    ],


    "Mesh::StructuredRegularFixedOfDimension" : [
        [ "1", "2", "3" ]
    ],
    "Mesh::StructuredDeformableOfDimension" : [
        [ "1", "2", "3" ]
    ],
    "Mesh::UnstructuredDeformableOfDimension" : [
        [ "1", "2", "3" ]
    ],


    "BasisFunction::CompletePolynomialOfDimensionAndOrder" : [
        [ "1", "2", "3" ],
        [ "0", "1", "2" ]
    ],
    "BasisFunction::Hermite" : [],
    "BasisFunction::LagrangeOfOrder" : [
        [ "0", "1" ]
    ],
    #"BasisFunction::Mixed" : [
    #    [ "LowOrderBasisFunction" ],
    #    [ "HighOrderBasisFunction" ]
    #],
    #"LowOrderBasisFunction" : [],
    #"HighOrderBasisFunction" : [],


    "Quadrature::ClenshawCurtis" : [
        [ "1", "2", "3", "4", "5", "6", "7", "64" ]
    ],
    "Quadrature::Gauss" : [
        [ "1" , "2" , "3", "4", "5", "6", "7", "8", "10", "12", "16", "20", "24", "64" ]    
    ],
    "Quadrature::NewtonCotes" : [
        [ "1", "2", "3", "4", "5", "6", "7", "8" ]
    ],
    "Quadrature::TensorProduct" : [
        [ "1", "2", "3" ],
        [ "Quadrature::" ]
    ],
    #"Quadrature::Mixed" : [
    #    [ "LowOrderQuadrature" ],
    #    [ "HighOrderQuadrature" ]
    #],
    #"LowOrderQuadrature" : [],
    #"HighOrderQuadrature" : [
    #    [
    #        "Quadrature::ClenshawCurtis",
    #        "Quadrature::Gauss",
    #        "Quadrature::NewtonCotes"
    #    ]
    #],


    "Equation::Dynamic::IsotropicDiffusion" : [],
    "Equation::Dynamic::AnisotropicDiffusion" : [],
    "Equation::Static::Laplace" : [],
    "Equation::Static::GeneralizedLaplace" : [],
    "Equation::Static::LinearElasticity" : [],
    "Equation::Static::LinearElasticityActiveStress" : [],
    #TODO are these correct?
    "Equation::SolidMechanics::MooneyRivlinIncompressible3D" : [],
    "Equation::SolidMechanics::TransverselyIsotropicMooneyRivlinIncompressible3D" : [],
    "Equation::SolidMechanics::TransverselyIsotropicMooneyRivlinIncompressibleActive3D" : [],
    "Equation::SolidMechanics::HyperelasticTendon" : [],
    "Equation::Static::Poisson" : [],
    "Equation::Static::GeneralizedPoisson" : [],
}
