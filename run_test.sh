rm ./shpwl.log
rm ./cong.log
python dreamplace/Placer.py test/idacs2022/mgc_matrix_mult_c.json
python dreamplace/Placer.py test/idacs2022/mgc_matrix_mult_c_route_opt.json
python dreamplace/Placer.py test/idacs2022/mgc_pci_bridge32_b.json
python dreamplace/Placer.py test/idacs2022/mgc_pci_bridge32_b_route_opt.json
python dreamplace/Placer.py test/idacs2022/mgc_superblue12.json
python dreamplace/Placer.py test/idacs2022/mgc_superblue12_route_opt.json
python dreamplace/Placer.py test/idacs2022/mgc_superblue16_a.json
python dreamplace/Placer.py test/idacs2022/mgc_superblue16_a_route_opt.json