/*****************************************************************************
 *
 * This file is part of Mapnik (c++ mapping toolkit)
 *
 * Copyright (C) 2024 Artem Pavlenko
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 *
 *****************************************************************************/

// mapnik
#include <mapnik/config.hpp>
#include "python_to_value.hpp"
#include "mapnik_value_converter.hpp"
#include <mapnik/util/variant.hpp>
#include <mapnik/feature.hpp>
#include <mapnik/expression.hpp>
#include <mapnik/expression_string.hpp>
#include <mapnik/expression_evaluator.hpp>
#include <mapnik/parse_path.hpp>
#include <mapnik/value.hpp>

//pybind11
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/stl_bind.h>

using mapnik::expression_ptr;
using mapnik::parse_expression;
using mapnik::to_expression_string;
using mapnik::path_expression_ptr;

namespace py = pybind11;

PYBIND11_MAKE_OPAQUE(mapnik::path_expression);

// expression
expression_ptr parse_expression_(std::string const& wkt)
{
    return parse_expression(wkt);
}

std::string expression_to_string_(mapnik::expr_node const& expr)
{
    return mapnik::to_expression_string(expr);
}

mapnik::value expression_evaluate_(mapnik::expr_node const& expr, mapnik::feature_impl const& f, py::dict const& d)
{
    // will be auto-converted to proper python type by `mapnik_value_to_python`
    return mapnik::util::apply_visitor(mapnik::evaluate<mapnik::feature_impl,
                                       mapnik::value,mapnik::attributes>(f, mapnik::dict2attr(d)),expr);
}

bool expression_evaluate_to_bool_(mapnik::expr_node const& expr, mapnik::feature_impl const& f, py::dict const& d)
{
    return mapnik::util::apply_visitor(mapnik::evaluate<mapnik::feature_impl,
                                       mapnik::value,mapnik::attributes>(f, mapnik::dict2attr(d)),expr).to_bool();
}

// path expression
path_expression_ptr parse_path_(std::string const& path)
{
    return mapnik::parse_path(path);
}

std::string path_to_string_(mapnik::path_expression const& expr)
{
    return mapnik::path_processor_type::to_string(expr);
}

std::string path_evaluate_(mapnik::path_expression const& expr, mapnik::feature_impl const& f)
{
    return mapnik::path_processor_type::evaluate(expr, f);
}

void export_expression(py::module const& m)
{
    py::class_<mapnik::expr_node, mapnik::expression_ptr>(m, "Expression")
        .def(py::init([] (std::string const& wkt) { return parse_expression_(wkt);}))
        .def("evaluate", &expression_evaluate_, py::arg("feature"), py::arg("variables") = py::dict())
        .def("to_bool", &expression_evaluate_to_bool_, py::arg("feature"), py::arg("variables") = py::dict())
        .def("__str__", &expression_to_string_);
    ;

    py::class_<mapnik::path_expression, mapnik::path_expression_ptr>(m, "PathExpression")
        .def(py::init([] (std::string const& wkt) { return parse_path_(wkt);}))
        .def("evaluate", &path_evaluate_)
        .def("__str__",&path_to_string_);
    ;

}
