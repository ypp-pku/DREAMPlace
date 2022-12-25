##
# @file   regression.py
# @author Jiaqi Gu
# @date   Aug 2021
#

import os
import sys
import numpy as np
import unittest
import logging
import time
import pdb

import torch
from torch.autograd import Function, Variable

sys.path.append(
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
        "dreamplace",
    )
)
import Placer
import Params
import configure

sys.path.pop()

designs = [
    "mgc_des_perf_1",
    "mgc_des_perf_a",
    "mgc_des_perf_b",
    "mgc_edit_dist_a",
    "mgc_fft_1",
    "mgc_fft_2",
    "mgc_fft_a",
    "mgc_fft_b",
    "mgc_matrix_mult_1",
    "mgc_matrix_mult_2",
    "mgc_matrix_mult_a",
    "mgc_matrix_mult_b",
    "mgc_matrix_mult_c",
    "mgc_pci_bridge32_a",
    "mgc_pci_bridge32_b",
    "mgc_superblue11_a",
    "mgc_superblue12",
    "mgc_superblue14",
    "mgc_superblue16_a",
    "mgc_superblue19",
]
# gpu flag
devices = ["cpu"]
if configure.compile_configurations["CUDA_FOUND"] == "TRUE" and torch.cuda.device_count():
    devices.append("gpu")
# deterministic flags
deterministics = ["deterministic", "indeterministic"]

# Yibo: I assume the results of different modes should be less than 0.5%
golden = {
    ("mgc_des_perf_1", "gpu", "deterministic"): {"GP": 5.473060e06, "LG": 5.623592e06, "DP": 5.533830e06},
    ("mgc_des_perf_1", "gpu", "indeterministic"): {"GP": 5.473060e06, "LG": 5.623592e06, "DP": 5.533830e06},
    ("mgc_des_perf_1", "cpu", "deterministic"): {"GP": 5.473060e06, "LG": 5.623592e06, "DP": 5.533830e06},
    ("mgc_des_perf_1", "cpu", "indeterministic"): {"GP": 5.473060e06, "LG": 5.623592e06, "DP": 5.533830e06},
    ("mgc_des_perf_a", "gpu", "deterministic"): {"GP": 1.099952e07, "LG": 1.134718e07, "DP": 1.112764e07},
    ("mgc_des_perf_a", "gpu", "indeterministic"): {"GP": 1.099952e07, "LG": 1.134718e07, "DP": 1.112764e07},
    ("mgc_des_perf_a", "cpu", "deterministic"): {"GP": 1.099952e07, "LG": 1.134718e07, "DP": 1.112764e07},
    ("mgc_des_perf_a", "cpu", "indeterministic"): {"GP": 1.099952e07, "LG": 1.134718e07, "DP": 1.112764e07},
    ("mgc_des_perf_b", "gpu", "deterministic"): {"GP": 9.084735e06, "LG": 9.294270e06, "DP": 9.017061e06},
    ("mgc_des_perf_b", "gpu", "indeterministic"): {"GP": 9.084735e06, "LG": 9.294270e06, "DP": 9.017061e06},
    ("mgc_des_perf_b", "cpu", "deterministic"): {"GP": 9.084735e06, "LG": 9.294270e06, "DP": 9.017061e06},
    ("mgc_des_perf_b", "cpu", "indeterministic"): {"GP": 9.084735e06, "LG": 9.294270e06, "DP": 9.017061e06},
    ("mgc_edit_dist_a", "gpu", "deterministic"): {"GP": 2.124074e07, "LG": 2.146746e07, "DP": 2.130998e07},
    ("mgc_edit_dist_a", "gpu", "indeterministic"): {"GP": 2.124074e07, "LG": 2.146746e07, "DP": 2.130998e07},
    ("mgc_edit_dist_a", "cpu", "deterministic"): {"GP": 2.124074e07, "LG": 2.146746e07, "DP": 2.130998e07},
    ("mgc_edit_dist_a", "cpu", "indeterministic"): {"GP": 2.124074e07, "LG": 2.146746e07, "DP": 2.130998e07},
    ("mgc_fft_1", "gpu", "deterministic"): {"GP": 2.076433e06, "LG": 2.119208e06, "DP": 2.066804e06},
    ("mgc_fft_1", "gpu", "indeterministic"): {"GP": 2.076433e06, "LG": 2.119208e06, "DP": 2.066804e06},
    ("mgc_fft_1", "cpu", "deterministic"): {"GP": 2.076433e06, "LG": 2.119208e06, "DP": 2.066804e06},
    ("mgc_fft_1", "cpu", "indeterministic"): {"GP": 2.076433e06, "LG": 2.119208e06, "DP": 2.066804e06},
    ("mgc_fft_2", "gpu", "deterministic"): {"GP": 1.872368e06, "LG": 1.918924e06, "DP": 1.868006e06},
    ("mgc_fft_2", "gpu", "indeterministic"): {"GP": 1.872368e06, "LG": 1.918924e06, "DP": 1.868006e06},
    ("mgc_fft_2", "cpu", "deterministic"): {"GP": 1.872368e06, "LG": 1.918924e06, "DP": 1.868006e06},
    ("mgc_fft_2", "cpu", "indeterministic"): {"GP": 1.872368e06, "LG": 1.918924e06, "DP": 1.868006e06},
    ("mgc_fft_a", "gpu", "deterministic"): {"GP": 3.117207e06, "LG": 3.190170e06, "DP": 3.138564e06},
    ("mgc_fft_a", "gpu", "indeterministic"): {"GP": 3.117207e06, "LG": 3.190170e06, "DP": 3.138564e06},
    ("mgc_fft_a", "cpu", "deterministic"): {"GP": 3.117207e06, "LG": 3.190170e06, "DP": 3.138564e06},
    ("mgc_fft_a", "cpu", "indeterministic"): {"GP": 3.117207e06, "LG": 3.190170e06, "DP": 3.138564e06},
    ("mgc_fft_b", "gpu", "deterministic"): {"GP": 4.176590e06, "LG": 4.273044e06, "DP": 4.232977e06},
    ("mgc_fft_b", "gpu", "indeterministic"): {"GP": 4.176590e06, "LG": 4.273044e06, "DP": 4.232977e06},
    ("mgc_fft_b", "cpu", "deterministic"): {"GP": 4.176590e06, "LG": 4.273044e06, "DP": 4.232977e06},
    ("mgc_fft_b", "cpu", "indeterministic"): {"GP": 4.176590e06, "LG": 4.273044e06, "DP": 4.232977e06},
    ("mgc_matrix_mult_1", "gpu", "deterministic"): {"GP": 1.066599e07, "LG": 1.090984e07, "DP": 1.065538e07},
    ("mgc_matrix_mult_1", "gpu", "indeterministic"): {"GP": 1.066599e07, "LG": 1.090984e07, "DP": 1.065538e07},
    ("mgc_matrix_mult_1", "cpu", "deterministic"): {"GP": 1.066599e07, "LG": 1.090984e07, "DP": 1.065538e07},
    ("mgc_matrix_mult_1", "cpu", "indeterministic"): {"GP": 1.066599e07, "LG": 1.090984e07, "DP": 1.065538e07},
    ("mgc_matrix_mult_2", "gpu", "deterministic"): {"GP": 1.083868e07, "LG": 1.108415e07, "DP": 1.082894e07},
    ("mgc_matrix_mult_2", "gpu", "indeterministic"): {"GP": 1.083868e07, "LG": 1.108415e07, "DP": 1.082894e07},
    ("mgc_matrix_mult_2", "cpu", "deterministic"): {"GP": 1.083868e07, "LG": 1.108415e07, "DP": 1.082894e07},
    ("mgc_matrix_mult_2", "cpu", "indeterministic"): {"GP": 1.083868e07, "LG": 1.108415e07, "DP": 1.082894e07},
    ("mgc_matrix_mult_a", "gpu", "deterministic"): {"GP": 1.467718e07, "LG": 1.538438e07, "DP": 1.517873e07},
    ("mgc_matrix_mult_a", "gpu", "indeterministic"): {"GP": 1.467718e07, "LG": 1.538438e07, "DP": 1.517873e07},
    ("mgc_matrix_mult_a", "cpu", "deterministic"): {"GP": 1.467718e07, "LG": 1.538438e07, "DP": 1.517873e07},
    ("mgc_matrix_mult_a", "cpu", "indeterministic"): {"GP": 1.467718e07, "LG": 1.538438e07, "DP": 1.517873e07},
    ("mgc_matrix_mult_b", "gpu", "deterministic"): {"GP": 1.507862e07, "LG": 1.608287e07, "DP": 1.577902e07},
    ("mgc_matrix_mult_b", "gpu", "indeterministic"): {"GP": 1.507862e07, "LG": 1.608287e07, "DP": 1.577902e07},
    ("mgc_matrix_mult_b", "cpu", "deterministic"): {"GP": 1.507862e07, "LG": 1.608287e07, "DP": 1.577902e07},
    ("mgc_matrix_mult_b", "cpu", "indeterministic"): {"GP": 1.507862e07, "LG": 1.608287e07, "DP": 1.577902e07},
    ("mgc_matrix_mult_c", "gpu", "deterministic"): {"GP": 1.455000e07, "LG": 1.558048e07, "DP": 1.526630e07},
    ("mgc_matrix_mult_c", "gpu", "indeterministic"): {"GP": 1.455000e07, "LG": 1.558048e07, "DP": 1.526630e07},
    ("mgc_matrix_mult_c", "cpu", "deterministic"): {"GP": 1.455000e07, "LG": 1.558048e07, "DP": 1.526630e07},
    ("mgc_matrix_mult_c", "cpu", "indeterministic"): {"GP": 1.455000e07, "LG": 1.558048e07, "DP": 1.526630e07},
    ("mgc_pci_bridge32_a", "gpu", "deterministic"): {"GP": 2.021039e06, "LG": 2.100235e06, "DP": 1.972106e06},
    ("mgc_pci_bridge32_a", "gpu", "indeterministic"): {"GP": 2.021039e06, "LG": 2.100235e06, "DP": 1.972106e06},
    ("mgc_pci_bridge32_a", "cpu", "deterministic"): {"GP": 2.021039e06, "LG": 2.100235e06, "DP": 1.972106e06},
    ("mgc_pci_bridge32_a", "cpu", "indeterministic"): {"GP": 2.021039e06, "LG": 2.100235e06, "DP": 1.972106e06},
    ("mgc_pci_bridge32_b", "gpu", "deterministic"): {"GP": 3.544777e06, "LG": 3.580610e06, "DP": 3.201317e06},
    ("mgc_pci_bridge32_b", "gpu", "indeterministic"): {"GP": 3.544777e06, "LG": 3.580610e06, "DP": 3.201317e06},
    ("mgc_pci_bridge32_b", "cpu", "deterministic"): {"GP": 3.544777e06, "LG": 3.580610e06, "DP": 3.201317e06},
    ("mgc_pci_bridge32_b", "cpu", "indeterministic"): {"GP": 3.544777e06, "LG": 3.580610e06, "DP": 3.201317e06},
    ("mgc_superblue11_a", "gpu", "deterministic"): {"GP": 3.480367e08, "LG": 3.609376e08, "DP": 3.512504e08},
    ("mgc_superblue11_a", "gpu", "indeterministic"): {"GP": 3.480367e08, "LG": 3.609376e08, "DP": 3.512504e08},
    ("mgc_superblue11_a", "cpu", "deterministic"): {"GP": 3.480367e08, "LG": 3.609376e08, "DP": 3.512504e08},
    ("mgc_superblue11_a", "cpu", "indeterministic"): {"GP": 3.480367e08, "LG": 3.609376e08, "DP": 3.512504e08},
    ("mgc_superblue12", "gpu", "deterministic"): {"GP": 2.552540e08, "LG": 2.621398e08, "DP": 2.572350e08},
    ("mgc_superblue12", "gpu", "indeterministic"): {"GP": 2.552540e08, "LG": 2.621398e08, "DP": 2.572350e08},
    ("mgc_superblue12", "cpu", "deterministic"): {"GP": 2.552540e08, "LG": 2.621398e08, "DP": 2.572350e08},
    ("mgc_superblue12", "cpu", "indeterministic"): {"GP": 2.552540e08, "LG": 2.621398e08, "DP": 2.572350e08},
    ("mgc_superblue14", "gpu", "deterministic"): {"GP": 2.270752e08, "LG": 2.320471e08, "DP": 2.299807E+08},
    ("mgc_superblue14", "gpu", "indeterministic"): {"GP": 2.270752e08, "LG": 2.320471e08, "DP": 2.299807E+08},
    ("mgc_superblue14", "cpu", "deterministic"): {"GP": 2.270752e08, "LG": 2.320471e08, "DP": 2.299807E+08},
    ("mgc_superblue14", "cpu", "indeterministic"): {"GP": 2.270752e08, "LG": 2.320471e08, "DP": 2.299807E+08},
    ("mgc_superblue16_a", "gpu", "deterministic"): {"GP": 2.653271e08, "LG": 2.731455e08, "DP": 2.685479e08},
    ("mgc_superblue16_a", "gpu", "indeterministic"): {"GP": 2.653271e08, "LG": 2.731455e08, "DP": 2.685479e08},
    ("mgc_superblue16_a", "cpu", "deterministic"): {"GP": 2.653271e08, "LG": 2.731455e08, "DP": 2.685479e08},
    ("mgc_superblue16_a", "cpu", "indeterministic"): {"GP": 2.653271e08, "LG": 2.731455e08, "DP": 2.685479e08},
    ("mgc_superblue19", "gpu", "deterministic"): {"GP": 1.548099e08, "LG": 1.579471e08, "DP": 1.560306E+08},
    ("mgc_superblue19", "gpu", "indeterministic"): {"GP": 1.548099e08, "LG": 1.579471e08, "DP": 1.560306E+08},
    ("mgc_superblue19", "cpu", "deterministic"): {"GP": 1.548099e08, "LG": 1.579471e08, "DP": 1.560306E+08},
    ("mgc_superblue19", "cpu", "indeterministic"): {"GP": 1.548099e08, "LG": 1.579471e08, "DP": 1.560306E+08},
}


class ISPD2015Test(unittest.TestCase):
    def testAll(self):
        metrics_list = {}
        for design in designs:
            json_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "%s.json" % (design))
            params = Params.Params()
            params.load(json_file)
            # control numpy multithreading
            os.environ["OMP_NUM_THREADS"] = "%d" % (params.num_threads)
            metrics_list[design] = []

            for device_name in ["gpu"]*5+["cpu"]*2:
                for deterministic_name in ["indeterministic"]:
                    params.gpu = 0 if device_name == "cpu" else 1
                    params.deterministic_flag = 0 if deterministic_name == "indeterministic" else 1
                    params.global_place_flag = 1
                    params.legalize_flag = 1
                    params.detaield_place_flag = 1
                    params.detailed_place_engine = ""
                    logging.info("%s, %s, %s" % (design, device_name, deterministic_name))
                    logging.info("parameters = %s" % (params))
                    # run placement
                    tt = time.time()
                    metrics = Placer.place(params)
                    logging.info("placement takes %.3f seconds" % (time.time() - tt))
                    # verify global placement results
                    metrics_list[design].append(
                        (
                            metrics[-3][-1][-1].hpwl.cpu().numpy(),
                            metrics[-2].hpwl.cpu().numpy(),
                            metrics[-1].hpwl.cpu().numpy(),
                        )
                    )
            m = np.array(metrics_list[design])
            metrics_list[design] = m
            gp, lg, dp = m[:, 0], m[:, 1], m[:, 2]
            gp_mean, lg_mean, dp_mean = np.mean(gp), np.mean(lg), np.mean(dp)
            rtol = lambda x, avg: max(avg-np.min(x), np.max(x)-avg)/avg
            gp_rtol, lg_rtol, dp_rtol = rtol(gp, gp_mean), rtol(lg, lg_mean), rtol(dp, dp_mean)
            logging.info(f"Avg metrics for {design}\n{m}\nGP={gp_mean:g} ({gp_rtol}), LG={lg_mean:g} ({lg_rtol}), DP={dp_mean:g} ({dp_rtol})")
        logging.info("Overall Summary")
        for design in designs:
            m = metrics_list[design]
            gp, lg, dp = m[:, 0], m[:, 1], m[:, 2]
            gp_mean, lg_mean, dp_mean = np.mean(gp), np.mean(lg), np.mean(dp)
            rtol = lambda x, avg: max(avg-np.min(x), np.max(x)-avg)/avg
            gp_rtol, lg_rtol, dp_rtol = rtol(gp, gp_mean), rtol(lg, lg_mean), rtol(dp, dp_mean)
            logging.info(f"Avg metrics for {design}\n{m}\nGP={gp_mean:g} ({gp_rtol}), LG={lg_mean:g} ({lg_rtol}), DP={dp_mean:g} ({dp_rtol})")



if __name__ == "__main__":
    """
    @brief main function to invoke the entire placement flow.
    """
    logging.root.name = "DREAMPlace"
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)-7s] %(name)s - %(message)s",
        filename="sensitivity_ispd2015.log",
    )

    unittest.main()
